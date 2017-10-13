//*****************************************************************************
//
//*****************************************************************************

#include "includes.h"

#define LED_RED_ON() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1,GPIO_PIN_1);}while(0)
#define LED_RED_OFF() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1,0);}while(0)
#define LED_RED_SWAP() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1,ROM_GPIOPinRead(GPIO_PORTF_BASE,GPIO_PIN_1)^GPIO_PIN_1);}while(0)

uint32_t g_ui32SysClock;

void init_board(void)
{
    // interrupts and clock system
    ROM_FPUEnable();
    ROM_FPULazyStackingEnable();
    //ROM_SysCtlClockSet(SYSCTL_SYSDIV_5 | SYSCTL_USE_PLL | SYSCTL_OSC_MAIN | SYSCTL_XTAL_16MHZ); // 40MHz
    ROM_SysCtlClockSet(SYSCTL_SYSDIV_2_5 | SYSCTL_USE_PLL | SYSCTL_OSC_MAIN | SYSCTL_XTAL_16MHZ); // 80MHz

    // peripherals
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOC);
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOD);
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);

    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0); // timer0

    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0); // output
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART1); // uart input 1
    ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART2); // uart input 2

    g_ui32SysClock = 80000000;//ROM_SysCtlClockGet();

    ROM_GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE,GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3);
    ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3,0x00);
}

//*****************************************************************************
//
// Main loop
//
//*****************************************************************************
int main(void)
{
    init_board();
    init_timer();

    uint32_t led_time = 0;

    // Loop forever.
    while(1) {
        g_loop_ms = millis();
        g_loop_us = micros();

        if ((g_loop_ms-led_time)>500) {
            LED_RED_SWAP();
            led_time = g_loop_ms;
        }
    }
}
