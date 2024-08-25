odoo.define('ab_inventory_adjust.barcode_reader', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const Helper = require('ab_inventory_adjust.helper_functions');

    FormController.include({
        start: function () {
            const res = this._super.apply(this, arguments);

            let PREFIXPressed = false;
            let keysSent = false;

            this.$el.on('keydown', async function (event) {

                if (event.key === Helper.PREFIX && !PREFIXPressed) {
                    PREFIXPressed = true;
                    keysSent = false;
                    event.preventDefault(); // Prevent default PREFIX behavior

                    const barcode = await Helper.collectBarcodeKeys();
                    PREFIXPressed = false; // Reset PREFIX flag after processing

                    await Helper.addLineIfNeeded();

                    document.activeElement.value = barcode;
                    document.activeElement.dispatchEvent(new Event('input', {bubbles: true}));

                    const itemsCount = await Helper.fetchDropdownItems(barcode);

                    if (itemsCount !== 1) return;

                    document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Tab',
                        code: 'Tab',
                        keyCode: 9,
                        which: 9,
                        bubbles: true
                    }));
                }
            });

            return res;
        }
    });
});
