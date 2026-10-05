"""Fixed credential-input diagnostics. Never attach the entered value."""


class HiddenInputUnavailable(ValueError):
    CODES = {'secure_tty_required', 'hidden_input_unavailable', 'input_ended',
             'email_invalid', 'token_empty', 'token_too_long', 'token_multiline'}

    def __init__(self, code):
        if code not in self.CODES:
            raise ValueError('Unknown input diagnostic')
        self.code = code
        super().__init__(code)
