#define TICKS_PER_MILLISEC 80000
#define TICKS_PER_MICROSEC 80

//*****************************************************************************
//
// The system clock frequency.
//
//*****************************************************************************
uint32_t g_ui32SysClock;

uint32_t g_loop_ms, g_loop_us;

void init_timer(void);
uint32_t millis(void);
uint32_t micros(void);
