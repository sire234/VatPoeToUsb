"""Status LED (B7, Rev 4f) - one plain green indicator LED on one GPIO
Block from: architecture/net_plan.md section "Rev 4d", B7 (Rev 4f change below)
Interface nets: GND, LED_DIN

Rev 4b replaced the discrete RGB LED D11 + Q2-Q4 + R38-R44 (Rev 2-4) by one addressable LED.
Rev 4f: the addressable WS2812B-2020-V6 is replaced by an ordinary green 0603 LED
(MEIHUA MHT193CGCT, 569 nm, Vf 2.2 V typ @ 5 mA). GPIO28 drives it active-high through R38:
GPIO28 -> R38 330R -> LED_DIN_R -> D11 anode, cathode -> GND.
I_F = (3.3 V - ~2.1 V) / 330 R ~ 3.5 mA (within the RP2040 4 mA default drive strength).
A low-Vf green (AlGaInP, ~570 nm) is used on purpose: InGaN "true green" LEDs need ~3 V
and leave no headroom on a 3.3 V GPIO. C64 (WS2812 decoupling) is removed.
Net names LED_DIN / LED_DIN_R are kept from Rev 4b so the layout stays unchanged.
Pinout: Device:LED pin 1 = K, pin 2 = A; LED_SMD:LED_0603_1608Metric pad 1 = K
(cathode mark on the green side of the part - check polarity in the JLC placement viewer).
"""
import os
os.environ.setdefault('KICAD10_SYMBOL_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
os.environ.setdefault('KICAD_SYMBOL_DIR',    r'C:\Program Files\KiCad\10.0\share\kicad\symbols')
from skidl import *
PROJECT_LIBS = r'C:\Users\simon\Documents\Projects\Test\PoeToUSB\libs'
if PROJECT_LIBS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(PROJECT_LIBS)


@SubCircuit
def status_led(gnd, led_din):
    """Green status LED, driven active-high by one 3.3 V GPIO (GPIO28).

    Args:
        gnd: Ground reference (LED cathode)
        led_din: GPIO28 line from U5 (high = LED on)
    """
    led_din_r = Net('LED_DIN_R')   # after the series resistor, at the LED anode

    # D11: green 0603 LED, 569 nm, Vf 2.2 V typ, 11.2 mcd @ 5 mA.
    d11 = Part('Device', 'LED', ref='D11', value='green',
               footprint='LED_SMD:LED_0603_1608Metric')
    d11.fields['MPN'] = 'MEIHUA MHT193CGCT'; d11.fields['LCSC'] = 'C2962098'
    d11['A'] += led_din_r   # anode (pin 2)
    d11['K'] += gnd         # cathode (pin 1)

    # R38: 330 R LED current limiting resistor (~3.5 mA).
    r38 = Part('Device', 'R', ref='R38', value='330R', footprint='Resistor_SMD:R_0402_1005Metric')
    r38.fields['MPN'] = '0402WGF3300TCE'; r38.fields['LCSC'] = 'C25104'
    r38[1] += led_din
    r38[2] += led_din_r
