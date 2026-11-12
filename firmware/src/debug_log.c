// Debug log: an extra stdio driver that copies every printf line (with uptime stamp) into a ring
// buffer. RTT output is unchanged. Over TCP the history can be read with "log" and live output
// switched on with "debug on" (lines "#DBG <stamp> <text>"), see net.c. So the debug output of a
// board in the field is visible without a debug probe (e.g. valve-scan --verbose).
//
// The ring holds complete lines only; when it is full the oldest lines are dropped. A reader keeps
// a cursor (sequence number of the next line); if its line was dropped it continues at the oldest.
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/stdio/driver.h"
#include "app.h"

#define RING_SIZE   4096
#define LINE_MAX    160

static char ring[RING_SIZE];
static size_t head, tail;               // byte positions: head = write, tail = oldest line
static uint32_t seq_head, seq_tail;     // line numbers: next to write, oldest kept

static char line[LINE_MAX];
static size_t line_len, stamp_len;
static bool line_open;

static size_t ring_used(void) {
    return (head + RING_SIZE - tail) % RING_SIZE;
}

static void drop_oldest(void) {
    while (tail != head && ring[tail] != '\n')
        tail = (tail + 1) % RING_SIZE;
    if (tail != head)
        tail = (tail + 1) % RING_SIZE;  // skip the '\n'
    seq_tail++;
}

static void commit_line(void) {
    line[line_len++] = '\n';
    while (RING_SIZE - 1 - ring_used() < line_len)
        drop_oldest();
    for (size_t i = 0; i < line_len; i++) {
        ring[head] = line[i];
        head = (head + 1) % RING_SIZE;
    }
    seq_head++;
    line_len = 0;
    line_open = false;
}

static void out_chars(const char *buf, int len) {
    for (int i = 0; i < len; i++) {
        char c = buf[i];
        if (c == '\r')
            continue;
        if (!line_open) {
            uint32_t ms = to_ms_since_boot(get_absolute_time());
            line_len = stamp_len = (size_t)snprintf(line, LINE_MAX, "%lu.%03lu ", (unsigned long)(ms / 1000),
                                                    (unsigned long)(ms % 1000));
            line_open = true;
        }
        if (c == '\n') {
            if (line_len == stamp_len)
                line_open = false;      // empty line (only the stamp): drop it
            else
                commit_line();
        }
        else if (line_len < LINE_MAX - 2)
            line[line_len++] = c;
    }
}

static stdio_driver_t driver = {
    .out_chars = out_chars,
#if PICO_STDIO_ENABLE_CRLF_SUPPORT
    .crlf_enabled = false,
#endif
};

void debug_log_init(void) {
    stdio_set_driver_enabled(&driver, true);
}

uint32_t debug_log_oldest(void) {
    return seq_tail;
}

uint32_t debug_log_newest(void) {
    return seq_head;
}

// copies line number *cursor (without '\n') into buf, advances *cursor; false if there is none
bool debug_log_read(uint32_t *cursor, char *buf, size_t size) {
    if ((int32_t)(*cursor - seq_tail) < 0)
        *cursor = seq_tail;             // dropped meanwhile: continue at the oldest line
    if (*cursor == seq_head)
        return false;

    size_t pos = tail;
    for (uint32_t s = seq_tail; s != *cursor; s++) {
        while (ring[pos] != '\n')
            pos = (pos + 1) % RING_SIZE;
        pos = (pos + 1) % RING_SIZE;
    }
    size_t n = 0;
    while (ring[pos] != '\n') {
        if (n < size - 1)
            buf[n++] = ring[pos];
        pos = (pos + 1) % RING_SIZE;
    }
    buf[n] = 0;
    (*cursor)++;
    return true;
}
