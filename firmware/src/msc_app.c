// USB stick: FatFs on the first mass storage device; everything app_emit() sends is appended to
// HIDLOG.TXT (complete lines, f_sync after each batch so pulling the stick loses little).
//
// FatFs needs blocking disk_read/disk_write, but TinyUSB transfers are asynchronous: the disk_*
// functions start a transfer and run tuh_task() until it completes. That is only safe from the
// main loop, so the TinyUSB callbacks here only set flags and msc_app_task() does the file work.
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/watchdog.h"
#include "tusb.h"
#include "ff.h"
#include "diskio.h"
#include "app.h"

#define LOG_FILE    "HIDLOG.TXT"
#define LOG_BUF     2048

static uint8_t msc_addr;                // device address of the stick, 0 = none
static bool mount_pending, unmount_pending, mounted;
static FATFS fs;
static FIL log_file;

static char log_buf[LOG_BUF];           // ring buffer, filled by app_emit()
static size_t log_head, log_tail;

static volatile bool io_busy, io_ok;

// ---- TinyUSB callbacks ----

void tuh_msc_mount_cb(uint8_t dev_addr) {
    printf("MSC: mount addr %u, %lu blocks x %lu bytes\n", dev_addr,
           (unsigned long)tuh_msc_get_block_count(dev_addr, 0),
           (unsigned long)tuh_msc_get_block_size(dev_addr, 0));
    if (msc_addr == 0) {
        msc_addr = dev_addr;
        mount_pending = true;
    } else {
        printf("MSC: only one stick is used, ignoring addr %u\n", dev_addr);
    }
}

void tuh_msc_umount_cb(uint8_t dev_addr) {
    printf("MSC: unmount addr %u\n", dev_addr);
    if (dev_addr == msc_addr) {
        msc_addr = 0;
        mounted = false;
        mount_pending = false;
        unmount_pending = true;
    }
}

// ---- log ----

void msc_log_queue(const char *s, size_t len) {
    if (!mounted)
        return;
    while (len--) {
        size_t next = (log_head + 1) % LOG_BUF;
        if (next == log_tail)
            return;                     // full: drop the rest
        log_buf[log_head] = *s++;
        log_head = next;
    }
}

bool msc_app_mounted(void) {
    return mounted;
}

static void mount_stick(void) {
    if (tuh_msc_get_block_size(msc_addr, 0) != FF_MAX_SS) {
        printf("MSC: block size %lu not supported\n", (unsigned long)tuh_msc_get_block_size(msc_addr, 0));
        return;
    }
    FRESULT r = f_mount(&fs, "", 1);
    if (r != FR_OK) {
        printf("MSC: f_mount failed (%d) - stick must be FAT16/FAT32 (no exFAT/NTFS)\n", r);
        return;
    }
    r = f_open(&log_file, LOG_FILE, FA_OPEN_APPEND | FA_WRITE);
    if (r != FR_OK) {
        printf("MSC: cannot open %s (%d)\n", LOG_FILE, r);
        f_mount(NULL, "", 0);
        return;
    }
    DWORD free_clusters;
    FATFS *pfs;
    if (f_getfree("", &free_clusters, &pfs) == FR_OK)
        printf("MSC: %s open, %lu MB free\n", LOG_FILE,
               (unsigned long)((uint64_t)free_clusters * pfs->csize * FF_MAX_SS / (1024 * 1024)));
    log_head = log_tail = 0;
    mounted = true;
    app_eventf("#LOG started, uptime %lu s\n", (unsigned long)(to_ms_since_boot(get_absolute_time()) / 1000));
}

static void flush_log(void) {
    // write up to the last complete line; the bytes are copied out first because the nested
    // tuh_task() in disk_write may add new HID data to the ring buffer meanwhile
    static char chunk[512];
    size_t n = 0, last_nl = 0;
    for (size_t i = log_tail; i != log_head && n < sizeof chunk; i = (i + 1) % LOG_BUF) {
        chunk[n++] = log_buf[i];
        if (log_buf[i] == '\n')
            last_nl = n;
    }
    if (last_nl == 0 && n < sizeof chunk)
        return;
    if (last_nl == 0)
        last_nl = n;                    // a line longer than the chunk: write it anyway
    log_tail = (log_tail + last_nl) % LOG_BUF;

    UINT written;
    if (f_write(&log_file, chunk, last_nl, &written) != FR_OK || written != last_nl || f_sync(&log_file) != FR_OK) {
        printf("MSC: write error, log stopped\n");
        mounted = false;
    }
}

void msc_app_task(void) {
    if (unmount_pending) {
        unmount_pending = false;
        f_mount(NULL, "", 0);           // no disk access, just forget the volume
    }
    if (mount_pending) {
        mount_pending = false;
        mount_stick();
    }
    if (mounted && log_tail != log_head)
        flush_log();
}

// ---- FatFs disk glue (drive 0 = msc_addr, LUN 0) ----

static bool io_complete(uint8_t dev_addr, const tuh_msc_complete_data_t *data) {
    io_ok = data->csw->status == MSC_CSW_STATUS_PASSED;
    io_busy = false;
    return true;
}

static DRESULT wait_io(void) {
    // no timeout: the loop ends when the transfer completes or the stick is removed
    // (tuh_msc_umount_cb clears msc_addr; TinyUSB then no longer touches the buffer)
    // (a large FAT32 stick can keep FatFs busy for seconds, e.g. f_getfree reading the whole FAT)
    while (io_busy && msc_addr) {
        watchdog_update();
        tuh_task();
    }
    return (!io_busy && io_ok) ? RES_OK : RES_ERROR;
}

DSTATUS disk_status(BYTE pdrv) {
    return (pdrv == 0 && msc_addr && tuh_msc_mounted(msc_addr)) ? 0 : STA_NODISK | STA_NOINIT;
}

DSTATUS disk_initialize(BYTE pdrv) {
    return disk_status(pdrv);
}

DRESULT disk_read(BYTE pdrv, BYTE *buff, LBA_t sector, UINT count) {
    if (disk_status(pdrv))
        return RES_NOTRDY;
    io_busy = true;
    if (!tuh_msc_read10(msc_addr, 0, buff, sector, (uint16_t)count, io_complete, 0)) {
        io_busy = false;
        return RES_ERROR;
    }
    return wait_io();
}

DRESULT disk_write(BYTE pdrv, const BYTE *buff, LBA_t sector, UINT count) {
    if (disk_status(pdrv))
        return RES_NOTRDY;
    io_busy = true;
    if (!tuh_msc_write10(msc_addr, 0, buff, sector, (uint16_t)count, io_complete, 0)) {
        io_busy = false;
        return RES_ERROR;
    }
    return wait_io();
}

DRESULT disk_ioctl(BYTE pdrv, BYTE cmd, void *buff) {
    if (disk_status(pdrv))
        return RES_NOTRDY;
    switch (cmd) {
    case CTRL_SYNC:
        return RES_OK;                  // writes are blocking
    case GET_SECTOR_COUNT:
        *(LBA_t *)buff = tuh_msc_get_block_count(msc_addr, 0);
        return RES_OK;
    case GET_SECTOR_SIZE:
        *(WORD *)buff = (WORD)tuh_msc_get_block_size(msc_addr, 0);
        return RES_OK;
    case GET_BLOCK_SIZE:
        *(DWORD *)buff = 1;
        return RES_OK;
    default:
        return RES_PARERR;
    }
}
