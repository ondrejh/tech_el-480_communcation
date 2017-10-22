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

#define UART1_AVAIL (UARTCharsAvail(UART1_BASE))
#define UART2_AVAIL (UARTCharsAvail(UART2_BASE))
#define UART1_GETC() (UARTCharGet(UART1_BASE))
#define UART2_GETC() (UARTCharGet(UART2_BASE))

#define OUTBUFLEN 256
#define INBUFLEN 256

#define MSG_TIMEOUT ((50*1000000)/9600)


void uart_printf(char *buf);
void uart_write_hex(uint32_t val,int len);
void uart_write_int(uint32_t val);

uint8_t outbuf[OUTBUFLEN];
int outbptri = 0, outbptro = 0;

uint8_t inbuf1[INBUFLEN], inbuf2[INBUFLEN];
uint32_t inbptri1 = 0, inbptri2 = 0, inbptro1 = 0, inbptro2 = 0;
uint32_t t_start1, t_start2;
uint32_t t_last1, t_last2;
bool busy1, busy2;

uint32_t g_ui32SysClock;

void uart_output_poll(void)
{
    if (outbptri!=outbptro) {
        if (!ROM_UARTSpaceAvail(UART0_BASE))
            return;
        uint8_t c;
        c = outbuf[outbptro++];
        ROM_UARTCharPut(UART0_BASE,c);
        outbptro%=OUTBUFLEN;
    }
}

void uart_input1_poll(void)
{
    if (UART1_AVAIL) {
        uint8_t c = UART1_GETC();
        inbuf1[inbptri1++] = c;
        inbptri1 %= INBUFLEN;
        t_last1 = g_loop_us;
        if (!busy1) {
            busy1 = true;
            LED_GREEN_ON();
            t_start1 = g_loop_ms;
        }
    }
    else {
        if (busy1) {
            if ((g_loop_us-t_last1)>MSG_TIMEOUT) { // end of rx detected
                uart_write_hex(t_start1,4);
                uart_printf(" U1");
                uart_printf(" (");
                uart_write_int((inbptri1-inbptro1)%INBUFLEN);
                uart_printf("):");
                int cnt = 0;
                while (inbptri1!=inbptro1) {
                    if ((cnt++&0x01)==0)
                        uart_printf(" ");
                    uart_write_hex(inbuf1[inbptro1++],2);
                    inbptro1 %= INBUFLEN;
                }
                busy1 = false;
                uart_printf("\n\r");
                LED_GREEN_OFF();
            }
        }
    }
}

void uart_input2_poll(void)
{
    if (UART2_AVAIL) {
        uint8_t c = UART2_GETC();
        inbuf2[inbptri2++] = c;
        inbptri2 %= INBUFLEN;
        t_last2 = g_loop_us;
        if (!busy2) {
            busy2 = true;
            LED_RED_ON();
            t_start2 = g_loop_ms;
        }
    }
    else {
        if (busy2) {
            if ((g_loop_us-t_last2)>MSG_TIMEOUT) { // end of rx detected
                uart_write_hex(t_start2,4);
                uart_printf(" U2");
                uart_printf(" (");
                uart_write_int((inbptri2-inbptro2)%INBUFLEN);
                uart_printf("):");
                int cnt = 0;
                while (inbptri2!=inbptro2) {
                    if ((cnt++&0x01)==0)
                        uart_printf(" ");
                    uart_write_hex(inbuf2[inbptro2++],2);
                    inbptro2 %= INBUFLEN;
                }
                busy2 = false;
                uart_printf("\n\r");
                LED_RED_OFF();
            }
        }
    }
}

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

void uart_putc(uint8_t c)
{
    outbuf[outbptri++] = c;
    outbptri%=OUTBUFLEN;
}

void uart_write(uint8_t *buf, int dlen)
{
    int i;
    for (i=0;i<dlen;i++) {
        uart_putc((uint8_t)*buf++);
        /*if (!ROM_UARTSpaceAvail(UART0_BASE))
            break;
        ROM_UARTCharPut(UART0_BASE,(uint8_t)*buf++);*/
    }
}

void uart_printf(char *buf)
{
    while (1) {
    //while (ROM_UARTSpaceAvail(UART0_BASE)) {
        char c = *buf++;
        if (c=='\0')
            break;
        uart_putc(c);
        //ROM_UARTCharPut(UART0_BASE, c);
    }
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

    uart_printf((char*)str);
}

void uart_write_int(uint32_t val)
{
    uint8_t str[11];
    uint8_t ptr = 9;
    str[10] = '\0';
    uint32_t v = val;
    do {
        str[ptr--] = (v%10)+'0';
        v/=10;
    } while (v>0);
    ptr++;
    uart_printf((char*)&str[ptr]);
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

    ROM_GPIOPinTypeGPIOOutput(GPIO_PORTA_BASE,GPIO_PIN_4);
    ROM_GPIOPinTypeGPIOInput(GPIO_PORTA_BASE,GPIO_PIN_3);
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

    // Loop forever.
    while(1) {
        g_loop_ms = millis();
        g_loop_us = micros();

        ROM_GPIOPinWrite(GPIO_PORTA_BASE,GPIO_PIN_4,ROM_GPIOPinRead(GPIO_PORTA_BASE,GPIO_PIN_3)?0:GPIO_PIN_4);

        uart_output_poll();
        uart_input1_poll();
        uart_input2_poll();
    }
}
