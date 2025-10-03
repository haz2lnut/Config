#include QMK_KEYBOARD_H

enum my_layers {
	_HZ2LUT,
	_QWERTY,
	_LOWER,
	_RAISE,
	_ADJUST,
	_L0CK,
};

enum my_keycodes {
	LANG1 = SAFE_RANGE,
	LANG2,
};

#define LOWER LT(_LOWER, KC_SPC)
#define RAISE OSL(_RAISE)
#define ZRADJ LT(_ADJUST, KC_0)
#define ESCADJ LT(_ADJUST, KC_ESC)
#define TMUX C(KC_B)
#define L0CK TG(_L0CK)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
	[_HZ2LUT] = LAYOUT(
			KC_Q,    KC_F,    KC_G,    KC_Y,    XXXXXXX,                   XXXXXXX, KC_V,    KC_X,    KC_H,    KC_W,
			KC_A,    KC_S,    KC_T,    KC_E,    XXXXXXX,                   XXXXXXX, KC_N,    KC_I,    KC_R,    KC_C,
			KC_K,    KC_M,    KC_D,    KC_O,    XXXXXXX, L0CK,    L0CK,    XXXXXXX, KC_P,    KC_U,    KC_L,    KC_B,
			XXXXXXX, XXXXXXX, XXXXXXX, KC_BSPC, LOWER,   LANG1,   LANG2,   RAISE,   OS_LSFT, OS_LCTL, OS_LALT, OS_LGUI
			),

	[_QWERTY] = LAYOUT(
			KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,                      KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,
			KC_A,    KC_S,    KC_D,    KC_F,    KC_G,                      KC_H,    KC_J,    KC_K,    KC_L,    XXXXXXX,
			KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    _______, _______, KC_N,    KC_M,    XXXXXXX, XXXXXXX, XXXXXXX,
			_______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
			),

	[_LOWER] = LAYOUT(
			KC_CIRC, KC_AT,   KC_PERC, KC_BSLS, _______,                   _______, KC_7,    KC_8,    KC_9,    KC_DLR, 
			KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, _______,                   _______, KC_4,    KC_5,    KC_6,    KC_TILD,
			KC_LBRC, KC_LCBR, KC_RCBR, KC_RBRC, _______, _______, _______, _______, KC_1,    KC_2,    KC_3,    KC_GRV,
			_______, _______, _______, KC_DEL,  _______, _______, _______, ZRADJ,   TMUX,    _______, _______, _______
			),

	[_RAISE] = LAYOUT(
			KC_QUES, KC_PIPE, KC_AMPR, KC_HASH, _______,                   _______, KC_COLN, KC_QUOT, KC_DQT,  KC_EXLM,
			KC_J,    KC_LPRN, KC_RPRN, KC_SCLN, _______,                   _______, KC_DOT,  KC_COMM, KC_UNDS, KC_Z,   
			KC_LT,   KC_SLSH, KC_MINS, KC_GT,   _______, _______, _______, _______, KC_EQL,  KC_PLUS, KC_ASTR, KC_TAB,
			_______, _______, _______, KC_ENT,  ESCADJ,  _______, _______, _______, CW_TOGG, _______, _______, _______
			),

	[_ADJUST] = LAYOUT(
			DM_RSTP, KC_BRID, KC_BRIU, KC_MPLY, _______,                   _______, KC_F7,   KC_F8,   KC_F9,   KC_F12,
			KC_HOME, KC_PGDN, KC_PGUP, KC_END,  _______,                   _______, KC_F4,   KC_F5,   KC_F6,   KC_F11,
			KC_MRWD, KC_VOLD, KC_VOLU, KC_MFFD, _______, _______, _______, _______, KC_F1,   KC_F2,   KC_F3,   KC_F10,
			DM_PLY1, DM_REC1, KC_INS,  _______, _______, _______, _______, _______, _______, KC_CAPS, DM_REC2, DM_PLY2
			),

	[_L0CK] = LAYOUT(
			XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
			XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
			XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, _______, _______, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
			XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX
			),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
	if(record->event.pressed) {
		switch(keycode) {
			case LANG1:
				tap_code16(C(KC_SPC));
			case LANG2:
				if (get_highest_layer(default_layer_state) == _HZ2LUT)
					set_single_persistent_default_layer(_QWERTY);
				else
					set_single_persistent_default_layer(_HZ2LUT);
				return false;
		}
	}
	return true;
}
