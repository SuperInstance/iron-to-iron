```c
/*
 * bottle-cli.c
 *
 * A tiny “bottle” message system for inter‑agent communication.
 * Each message is a JSON file stored under the user’s home directory:
 *
 *   ~/.bottle/
 *       config.json          – stores last‑receive timestamp
 *       outbox/              – messages this agent has sent
 *       inbox/               – messages received from others
 *       archive/             – archived messages
 *
 * Compile:
 *     gcc -Wall -O2 -o bottle bottle-cli.c
 *
 * Usage (see the README in the original specification):
 *
 *   bottle send <to> <message>
 *   bottle receive
 *   bottle list
 *   bottle read <id>
 *   bottle reply <id> <message>
 *   bottle broadcast <message>
 *   bottle archive <id>
 *   bottle status
 *
 * The program deliberately avoids external JSON libraries – it builds
 * and parses the very small JSON structures required for the task
 * using plain string functions.
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>

#define CONFIG_FILE   "config.json"
#define OUTBOX_DIR    "outbox"
#define INBOX_DIR     "inbox"
#define ARCHIVE_DIR   "archive"

#define MAX_PATH 1024
#define MAX_JSON 4096
#define MAX_ID   64
#define MAX_LINE 256

/* -------------------------------------------------------------------------- */
/* Helper functions                                                          */
/* -------------------------------------------------------------------------- */

/* Return the full path to ~/.bottle/<subdir> (or the file itself). */
static void get_path(char *dest, const char *subdir, const char *file)
{
    const char *home = getenv("HOME");
    if (!home) home = ".";               /* fallback – should never happen */
    if (subdir) {
        if (file)
            snprintf(dest, MAX_PATH, "%s/.bottle/%s/%s", home, subdir, file);
        else
            snprintf(dest, MAX_PATH, "%s/.bottle/%s", home, subdir);
    } else {
        if (file)
            snprintf(dest, MAX_PATH, "%s/.bottle/%s", home, file);
        else
            snprintf(dest, MAX_PATH, "%s/.bottle", home);
    }
}

/* Ensure that a directory exists (create it if missing). */
static void ensure_dir(const char *path)
{
    struct stat st;
    if (stat(path, &st) == -1) {
        if (mkdir(path, 0700) == -1) {
            perror("mkdir");
            exit(EXIT_FAILURE);
        }
    } else if (!S_ISDIR(st.st_mode)) {
        fprintf(stderr, "%s exists but is not a directory\n", path);
        exit(EXIT_FAILURE);
    }
}

/* Initialise the directory hierarchy on first run. */
static void init_storage(void)
{
    char path[MAX_PATH];

    get_path(path, NULL, NULL);
    ensure_dir(path);

    get_path(path, OUTBOX_DIR, NULL);
    ensure_dir(path);
    get_path(path, INBOX_DIR, NULL);
    ensure_dir(path);
    get_path(path, ARCHIVE_DIR, NULL);
    ensure_dir(path);
}

/* Generate a pseudo‑unique ID: <epoch>-<pid>-<rand>. */
static void generate_id(char *buf, size_t buflen)
{
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    snprintf(buf, buflen, "%ld-%d-%04x", ts.tv_sec, getpid(),
             (unsigned)rand() & 0xFFFF);
}

/* Return current time in ISO‑8601 format (UTC). */
static void iso_timestamp(char *buf, size_t buflen)
{
    time_t now = time(NULL);
    struct tm tm;
    gmtime_r(&now, &tm);
    strftime(buf, buflen, "%Y-%m-%dT%H:%M:%SZ", &tm);
}

/* Load the config file (only the last‑receive timestamp is needed). */
static time_t load_last_receive(void)
{
    char path[MAX_PATH];
    FILE *fp;
    char line[MAX_LINE];
    time_t t = 0;

    get_path(path, NULL, CONFIG_FILE);
    fp = fopen(path, "r");
    if (!fp) return 0;               /* no config yet – treat as never received */

    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "\"last_receive\"")) {
            char *p = strchr(line, ':');
            if (p) {
                t = (time_t)atoll(p + 1);
                break;
            }
        }
    }
    fclose(fp);
    return t;
}

/* Save the last‑receive timestamp to the config file. */
static void save_last_receive(time_t t)
{
    char path[MAX_PATH];
    FILE *fp;

    get_path(path, NULL, CONFIG_FILE);
    fp = fopen(path, "w");
    if (!fp) {
        perror("fopen config");
        return;
    }
    fprintf(fp, "{\n  \"last_receive\": %ld\n}\n", (long)t);
    fclose(fp);
}

/* Write a JSON message to the outbox (or inbox when receiving). */
static void write_message(const char *dir, const char *id,
                          const char *from, const char *to,
                          const char *priority, const char *type,
                          const char *payload, int ttl)
{
    char path[MAX_PATH];
    char timestamp[32];
    FILE *fp;

    iso_timestamp(timestamp, sizeof(timestamp));

    get_path(path, dir, id);
    fp = fopen(path, "w");
    if (!fp) {
        perror("fopen message");
        exit(EXIT_FAILURE);
    }

    fprintf(fp,
            "{\n"
            "  \"id\": \"%s\",\n"
            "  \"from\": \"%s\",\n"
            "  \"to\": \"%s\",\n"
            "  \"priority\": \"%s\",\n"
            "  \"type\": \"%s\",\n"
            "  \"payload\": \"%s\",\n"
            "  \"timestamp\": \"%s\",\n"
            "  \"ttl\": %d,\n"
            "  \"replies\": []\n"
            "}\n",
            id, from, to, priority, type, payload, timestamp, ttl);
    fclose(fp);
}

/* Simple extraction of a JSON string value: "key":"value". */
static int json_get_string(const char *json, const char *key, char *out, size_t outlen)
{
    char pattern[64];
    const char *p;
    const char *start, *end;

    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    p = strstr(json, pattern);
    if (!p) return 0;
    p = strchr(p, ':');
    if (!p) return 0;
    p = strchr(p, '\"');
    if (!p) return 0;
    start = p + 1;
    end = strchr(start, '\"');
    if (!end) return 0;
    if ((size_t)(end - start) >= outlen) return 0;
    memcpy(out, start, end - start);
    out[end - start] = '\0';
    return 1;
}

/* -------------------------------------------------------------------------- */
/* Command implementations                                                    */
/* -------------------------------------------------------------------------- */

static const char *AGENT_NAME = "local-agent";   /* could be read from config */

static void cmd_send(const char *to, const char *msg)
{
    char id[MAX_ID];
    generate_id(id, sizeof(id));
    write_message(OUTBOX_DIR, id, AGENT_NAME, to,
                  "NORMAL", "TASK", msg, 3600);
    printf("Sent bottle %s to %s\n", id, to);
}

static void cmd_receive(void)
{
    char inbox_path[MAX_PATH];
    DIR *dir;
    struct dirent *ent;
    time_t last = load_last_receive();
    time_t newest = last;

    get_path(inbox_path, INBOX_DIR, NULL);
    dir = opendir(inbox_path);
    if (!dir) {
        perror("opendir inbox");
        return;
    }

    while ((ent = readdir(dir))) {
        struct stat st;
        char file_path[MAX_PATH];
        if (ent->d_name[0] == '.') continue;   /* skip . and .. */
        snprintf(file_path, sizeof(file_path), "%s/%s", inbox_path, ent->d_name);
        if (stat(file_path, &st) == -1) continue;
        if (st.st_mtime > last) {
            printf("New bottle: %s (received %ld)\n", ent->d_name, (long)st.st_mtime);
            if (st.st_mtime > newest) newest = st.st_mtime;
        }
    }
    closedir(dir);
    if (newest > last) save_last_receive(newest);
}

static void cmd_list(void)
{
    char inbox_path[MAX_PATH];
    DIR *dir;
    struct dirent *ent;

    get_path(inbox_path, INBOX_DIR, NULL);
    dir = opendir(inbox_path);
    if (!dir) {
        perror("opendir inbox");
        return;
    }

    printf("Inbox contents:\n");
    while ((ent = readdir(dir))) {
        if (ent->d_name[0] == '.') continue;
        printf("  %s\n", ent->d_name);
    }
    closedir(dir);
}

static void cmd_read(const char *id)
{
    char path[MAX_PATH];
    FILE *fp;
    char buffer[MAX_JSON];

    get_path(path, INBOX_DIR, id);
    fp = fopen(path, "r");
    if (!fp) {
        perror("fopen");
        return;
    }
    fread(buffer, 1, sizeof(buffer) - 1, fp);
    buffer[sizeof(buffer) - 1] = '\0';
    fclose(fp);
    printf("%s\n", buffer);
}

static void cmd_reply(const char *id, const char *msg)
{
    char path[MAX_PATH];
    FILE *fp;
    char buffer[MAX_JSON];
    char orig_from[MAX_LINE];
    char reply_id[MAX_ID];

    /* Load original message to discover the sender */
    get_path(path, INBOX_DIR, id);
    fp = fopen(path, "r");
    if (!fp) {
        perror("fopen original");
        return;
    }
    fread(buffer, 1, sizeof(buffer) - 1, fp);
    buffer[sizeof(buffer) - 1] = '\0';
    fclose(fp);

    if (!json_get_string(buffer, "from", orig_from, sizeof(orig_from))) {
        fprintf(stderr, "Could not parse original message\n");
        return;
    }

    generate_id(reply_id, sizeof(reply_id));
    write_message(OUTBOX_DIR, reply_id, AGENT_NAME, orig_from,
                  "NORMAL", "RESULT", msg, 3600);
    printf("Replied with bottle %s to %s\n", reply_id, orig_from);
}

static void cmd_broadcast(const char *msg)
{
    char id[MAX_ID];
    generate_id(id, sizeof(id));
    write_message(OUTBOX_DIR, id, AGENT_NAME, "ALL",
                  "NORMAL", "ALERT", msg, 3600);
    printf("Broadcast bottle %s\n", id);
}

static void cmd_archive(const char *id)
{
    char src[MAX_PATH], dst[MAX_PATH];
    get_path(src, INBOX_DIR, id);
    get_path(dst, ARCHIVE_DIR, id);
    if (rename(src, dst) == -1) {
        perror("rename");
        return;
    }
    printf("Archived bottle %s\n", id);
}

static void cmd_status(void)
{
    char path[MAX_PATH];
    struct stat st;
    int outbox = 0, inbox = 0, archive = 0;

    get_path(path, OUTBOX_DIR, NULL);
    DIR *d = opendir(path);
    if (d) {
        struct dirent *e;
        while ((e = readdir(d))) if (e->d_name[0] != '.') outbox++;
        closedir(d);
    }

    get_path(path, INBOX_DIR, NULL);
    d = opendir(path);
    if (d) {
        struct dirent *e;
        while ((e = readdir(d))) if (e->d_name[0] != '.') inbox++;
        closedir(d);
    }

    get_path(path, ARCHIVE_DIR, NULL);
    d = opendir(path);
    if (d) {
        struct dirent *e;
        while ((e = readdir(d))) if (e->d_name[0] != '.') archive++;
        closedir(d);
    }

    printf("Bottle system status:\n");
    printf("  Outbox : %d messages\n", outbox);
    printf("  Inbox  : %d messages\n", inbox);
    printf("  Archive: %d messages\n", archive);
}

/* -------------------------------------------------------------------------- */
/* Main entry point                                                          */
/* -------------------------------------------------------------------------- */

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr,
                "Usage: %s <command> [args]\n"
                "Commands:\n"
                "  send <to> <message>\n"
                "  receive\n"
                "  list\n"
                "  read <id>\n"
                "  reply <id> <message>\n"
                "  broadcast <message>\n"
                "  archive <id>\n"
                "  status\n",
                argv[0]);
        return EXIT_FAILURE;
    }

    srand((unsigned)time(NULL) ^ (unsigned)getpid());
    init_storage();

    if (strcmp(argv[1], "send") == 0) {
        if (argc != 4) {
            fprintf(stderr, "send requires <to> <message>\n");
            return EXIT_FAILURE;
        }
        cmd_send(argv[2], argv[3]);
    } else if (strcmp(argv[1], "receive") == 0) {
        cmd_receive();
    } else if (strcmp(argv[1], "list") == 0) {
        cmd_list();
    } else if (strcmp(argv[1], "read") == 0) {
        if (argc != 3) {
            fprintf(stderr, "read requires <id>\n");
            return EXIT_FAILURE;
        }
        cmd_read(argv[2]);
    } else if (strcmp(argv[1], "reply") == 0) {
        if (argc != 4) {
            fprintf(stderr, "reply requires <id> <message>\n");
            return EXIT_FAILURE;
        }
        cmd_reply(argv[2], argv[3]);
    } else if (strcmp(argv[1], "broadcast") == 0) {
        if (argc != 3) {
            fprintf(stderr, "broadcast requires <message>\n");
            return EXIT_FAILURE;
        }
        cmd_broadcast(argv[2]);
    } else if (strcmp(argv[1], "archive") == 0) {
        if (argc != 3) {
            fprintf(stderr, "archive requires <id>\n");
            return EXIT_FAILURE;
        }
        cmd_archive(argv[2]);
    } else if (strcmp(argv[1], "status") == 0) {
        cmd_status();
    } else {
        fprintf(stderr, "Unknown command: %s\n", argv[1]);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```