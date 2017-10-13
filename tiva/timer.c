#include "includes.h"

uint32_t g_loop_ms=0, g_loop_us=0;

void init_timer(void)
{
    // peripheral
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0); // timer0

    // free running timer
    ROM_TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC_UP);
    ROM_TimerEnable(TIMER0_BASE, TIMER_A);
}

uint32_t millis(void)
{
    static uint32_t last_ticks = 0;
    static uint32_t value = 0;

    uint32_t ticks, dmillis;

    ticks = ROM_TimerValueGet(TIMER0_BASE, TIMER_A);
    dmillis = (ticks - last_ticks) / TICKS_PER_MILLISEC;
    last_ticks += dmillis*TICKS_PER_MILLISEC;

    value += dmillis;

    return value;
}

uint32_t micros(void)
{
    static uint32_t last_ticks = 0;
    static uint32_t value = 0;

    uint32_t ticks, dmicros;

    ticks = ROM_TimerValueGet(TIMER0_BASE, TIMER_A);
    dmicros = (ticks - last_ticks) / TICKS_PER_MICROSEC;
    last_ticks += dmicros*TICKS_PER_MICROSEC;

    value += dmicros;

    return value;
}
