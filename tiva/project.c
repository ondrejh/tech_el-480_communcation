//*****************************************************************************
//
//*****************************************************************************

#include "includes.h"

#define LED_RED_ON() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1,GPIO_PIN_1);}while(0)
#define LED_RED_OFF() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1,0);}while(0)
#define LED_RED_SWAP() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_1,ROM_GPIOPinRead(GPIO_PORTF_BASE,GPIO_PIN_1)^GPIO_PIN_1);}while(0)

#define LED_GREEN_ON() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_3,GPIO_PIN_3);}while(0)
#define LED_GREEN_OFF() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_3,0);}while(0)
#define LED_GREEN_SWAP() do{ROM_GPIOPinWrite(GPIO_PORTF_BASE,GPIO_PIN_3,ROM_GPIOPinRead(GPIO_PORTF_BASE,GPIO_PIN_3)^GPIO_PIN_3);}while(0)

uint32_t g_ui32SysClock;

void uart_output_init(void)
{
    //ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    //ROM_GPIOPinConfigure(GPIO_PA0_U0RX);
    ROM_GPIOPinConfigure(GPIO_PA1_U0TX);

    //ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    MAP_GPIOPadConfigSet(GPIO_PORTA_BASE,GPIO_PIN_0|GPIO_PIN_1,GPIO_STRENGTH_2MA,GPIO_PIN_TYPE_STD_WPU);
    ROM_UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock,115200,UART_CONFIG_WLEN_8|UART_CONFIG_PAR_NONE|UART_CONFIG_STOP_ONE);
    ROM_GPIOPinTypeUART(GPIO_PORTA_BASE, /*GPIO_PIN_0 |*/ GPIO_PIN_1);

    ROM_UARTEnable(UART0_BASE);
}

void uart_input1_init(void)
{
    //ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART7);
    //ROM_UARTTxIntModeSet(UART1_BASE, UART_TXINT_MODE_EOT);
    ROM_UARTConfigSetExpClk(UART1_BASE, g_ui32SysClock, 9600, UART_CONFIG_WLEN_8|UART_CONFIG_STOP_ONE); // !! no 1.5 stop bits support

    //ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    ROM_GPIOPinConfigure(GPIO_PB0_U1RX);
    //ROM_GPIOPinConfigure(GPIO_PB1_U1TX);
    ROM_GPIOPinTypeUART(GPIO_PORTB_BASE, GPIO_PIN_0);// | GPIO_PIN_1);
}

void uart_input2_init(void)
{
    //ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART7);
    //ROM_UARTTxIntModeSet(UART2_BASE, UART_TXINT_MODE_EOT);
    ROM_UARTConfigSetExpClk(UART2_BASE, g_ui32SysClock, 9600, UART_CONFIG_WLEN_8|UART_CONFIG_STOP_ONE); // !! no 1.5 stop bits support

    //ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    ROM_GPIOPinConfigure(GPIO_PD6_U2RX);
    //ROM_GPIOPinConfigure(GPIO_PD7_U2TX);
    ROM_GPIOPinTypeUART(GPIO_PORTD_BASE, GPIO_PIN_6);// | GPIO_PIN_7);
}

#define UART1_AVAIL (UARTCharsAvail(UART1_BASE))
#define UART2_AVAIL (UARTCharsAvail(UART2_BASE))
#define UART1_GETC() (UARTCharGet(UART1_BASE))
#define UART2_GETC() (UARTCharGet(UART2_BASE))

void uart_write(uint8_t *buf, int dlen)
{
    int i;
    for (i=0;i<dlen;i++)
        ROM_UARTCharPut(UART0_BASE,(uint8_t)*buf++);
}

void uart_write_hex(uint32_t val,int len)
{
    uint8_t str[9];
    int l = len;
    if (l>8) l = 8;
    if (l<1) l = 1;

    uint32_t v = val;
    int i;
    for (i=l;i>0;i--) {
        str[i-1]=v&0xF;
        v>>=4;
        if (str[i-1]>9)
            str[i-1]+=('A'-10);
        else
            str[i-1]+='0';
    }
    str[l] = '\0';

    uart_write(str, l);
}

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

    uart_output_init();
    uart_input1_init();
    uart_input2_init();

    int lastRx = 0;
    int cnt = 0;

    // Loop forever.
    while(1) {
        g_loop_ms = millis();
        g_loop_us = micros();

        if (UART1_AVAIL) {
            if (lastRx!=1) {
                if (lastRx!=0)
                    uart_write((uint8_t *)"\n\r", 2);
                uart_write((uint8_t *)"U1:", 3);
                cnt = 0;
                lastRx = 1;
            }
            if (!(cnt&0x01))
                uart_write((uint8_t *)" ", 1);
            uart_write_hex(UART1_GETC(), 2);
            cnt++;
            LED_RED_ON();
            LED_GREEN_OFF();
        }

        if (UART2_AVAIL) {
            if (lastRx!=2) {
                if (lastRx!=0)
                    uart_write((uint8_t *)"\n\r", 2);
                uart_write((uint8_t *)"U2:", 3);
                cnt = 0;
                lastRx = 2;
            }
            if (!(cnt&0x01))
                uart_write((uint8_t *)" ", 1);
            uart_write_hex(UART2_GETC(), 2);
            cnt++;
            LED_RED_OFF();
            LED_GREEN_ON();
        }
    }
}
