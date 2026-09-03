/* Presentation-only FFT view selection. No guest memory or code changes. */
#include "mod_plugins.h"
#include <stdlib.h>

static void fft_widescreen_activate(void) {
    if (!psx_mod_set_fixed_display_aspect(16, 9)) abort();
    psx_mod_set_vertical_gradient_reveal(1);
}

PSX_MOD_CONSTRUCTOR(fft_register_widescreen) {
    if (!psx_mod_register_activation_plugin("fft.widescreen", fft_widescreen_activate))
        abort();
}
