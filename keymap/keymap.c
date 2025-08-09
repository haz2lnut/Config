#include QMK_KEYBOARD_H

enum my_layers {
	_BASE,
	_QWERTY,
	_LOWER,
	_RAISE,
	_ADJUST,
};

enum my_keycodes {
	LANG1 = SAFE_RANGE,
	LANG2,
	HEX1,
	HEX2,
};

#define LOWER OSL(_LOWER)
#define RAISE OSL(_RAISE)
#define ADJUST MO(_ADJUST)
#define TABADJ LT(_ADJUST, KC_TAB)
#define BSPCSFT SFT_T(KC_BSPC)
#define SPCSFT SFT_T(KC_SPC)
#define TMUX C(KC_B)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
	[_BASE] = LAYOUT(
			KC_Q,    KC_F,    KC_G,    KC_Y,    KC_AT,                     KC_GRV,  KC_V,    KC_X,    KC_H,    KC_W,
			KC_A,    KC_S,    KC_T,    KC_E,    KC_J,                      KC_Z,    KC_N,    KC_I,    KC_R,    KC_C,
			KC_K,    KC_M,    KC_D,    KC_O,    KC_ENT,  _______, _______, KC_COMM, KC_P,    KC_U,    KC_L,    KC_B,
			OS_LGUI, OS_LALT, OS_LCTL, RAISE,   LOWER,   LANG1,   LANG2,   SPCSFT,  BSPCSFT, OS_RCTL, OS_RALT, OS_RGUI
			),

	[_QWERTY] = LAYOUT(
			KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,                      KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,
			KC_A,    KC_S,    KC_D,    KC_F,    KC_G,                      KC_H,    KC_J,    KC_K,    KC_L,    KC_QUOT,
			KC_Z,    KC_X,    KC_C,    KC_V,    KC_ENT,  _______, _______, KC_COMM, KC_B,    KC_N,    KC_M,    KC_DOT,
			_______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
			),

	[_LOWER] = LAYOUT(
			KC_LBRC, KC_LCBR, KC_RCBR, KC_RBRC, KC_DLR,                    KC_CIRC, KC_HASH, KC_ASTR, KC_SLSH, KC_BSLS,
			KC_LT,   KC_PLUS, KC_MINS, KC_GT,   KC_AMPR,                   KC_PIPE, KC_EQL,  KC_UNDS, KC_DQT,  KC_DOT,
			KC_QUES, KC_LPRN, KC_RPRN, KC_SCLN, KC_ESC,  _______, _______, TMUX,    KC_COLN, KC_PERC, KC_QUOT, KC_EXLM,
			KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, _______, _______, _______, KC_TAB,  KC_DEL, _______, _______, _______
			),

	[_RAISE] = LAYOUT(
			KC_HOME, KC_PGDN, KC_PGUP, KC_END,  KC_BRIU,                   S(KC_E), KC_7,    KC_8,    KC_9,    S(KC_F),
			KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, KC_MPLY,                   S(KC_C), KC_4,    KC_5,    KC_6,    S(KC_D),
			KC_MRWD, KC_VOLD, KC_VOLU, KC_MFFD, KC_BRID, _______, _______, S(KC_A), KC_1,    KC_2,    KC_3,    S(KC_B),
			_______, _______, _______, _______, ADJUST,  _______, _______, _______, KC_DOT,  KC_0,    HEX1,    HEX2
			),

	[_ADJUST] = LAYOUT(
			_______, _______, _______, _______, _______,                   KC_F14,  KC_F7,   KC_F8,   KC_F9,   KC_F15,
			_______, _______, _______, _______, _______,                   KC_F12,  KC_F4,   KC_F5,   KC_F6,   KC_F13,
			KC_INS,  KC_CAPS, _______, _______, _______, _______, _______, KC_F10,  KC_F1,   KC_F2,   KC_F3,   KC_F11,
			_______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
			),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
	if (record->event.pressed) {
		switch (keycode) {
			case LANG1:
				tap_code16(LCTL(KC_SPC));
			case LANG2:
				if (get_highest_layer(default_layer_state) == _BASE)
					set_single_persistent_default_layer(_QWERTY);
				else
					set_single_persistent_default_layer(_BASE);
				return false;
			case HEX1:
				tap_code16(KC_0);
				tap_code16(KC_X);
				return false;
			case HEX2:
				tap_code16(KC_BSLS);
				tap_code16(KC_X);
				return false;
		}
	}
	return true;
}
