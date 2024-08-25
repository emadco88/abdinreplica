odoo.define('ab_inventory_adjust.barcode_reader', function (require) {
    "use strict";
    const rpc = require("web.rpc");
    const FormController = require('web.FormController');

    // Utility function to pause execution for a given number of milliseconds
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

// Function to perform the RPC call
    async function performSearch(barcode) {
        try {
            return await rpc.query({
                model: 'ab_product',  // Model name
                method: 'search_read',
                args: [[['barcode_ids', '=ilike', barcode]]], // Domain for search
                kwargs: {fields: ['id']}  // Fields to return
            });
        } catch (error) {
            console.error('Error performing search:', error);
            throw error;
        }
    }

    async function fetchDropdownItems(barcode) {
        const maxWaitTime = 3000; // Maximum wait time in milliseconds (3 seconds)
        const checkInterval = 50; // Interval between checks in milliseconds
        let elapsedTime = 0; // Time elapsed so far

        while (elapsedTime < maxWaitTime) {
            // Get all the <li> elements with class 'ui-menu-item'
            let listItems = document.querySelectorAll('a.dropdown-item.ui-menu-item-wrapper');
            let noResultItems = document.querySelectorAll('li.o_m2o_no_result.ui-menu-item');

            // Check if 'No records' item is present
            if (noResultItems.length > 0) {

                return 0;
            }

            // Return the count of <li> elements if they are present
            if (listItems.length > 0) {
                const rpcItems = await performSearch(barcode);
                const rpcItemsCount = rpcItems.length;
                console.log('rpcItemsCount', rpcItemsCount);
                if (listItems.length !== rpcItemsCount) {
                    await sleep(500);
                }
                return rpcItemsCount
            }

            await sleep(checkInterval);
            elapsedTime += checkInterval;
        }

        return 0; // Return 0 if the timeout is reached and no items are found
    }

    // Function to collect barcode keys
    function collectBarcodeKeys() {
        return new Promise(resolve => {
            let keys = [];

            // Handler for keydown events
            const barcodeKeyListener = function (event) {
                // Skip F10 key itself
                if (event.key !== 'F10') {
                    event.preventDefault(); // Prevent default action for all keys

                    const activeElement = document.activeElement;

                    // Check if the active element has the class 'o_field_many2one_selection'
                    const isInMany2OneSelection = activeElement.classList.contains('ui-autocomplete-input');
                    if (event.key === 'F8') {
                        if (!isInMany2OneSelection) {
                            // Click the link with class 'o_field_x2many_list_row_add' if F8 is pressed and conditions are met
                            const addButton = document.querySelector('.o_field_x2many_list_row_add a');
                            if (addButton) {
                                addButton.click();
                            } else {
                                console.warn('Add button not found');
                            }
                        }
                    } else if (event.key === 'Enter') {
                        // DO NOTHING
                    } else {
                        // Collect other keys
                        keys.push(event.key);
                    }
                }
            };

            // Listen for keydown events
            document.addEventListener('keydown', barcodeKeyListener);

            // Stop listening and resolve the promise after a delay
            sleep(200).then(() => {
                document.removeEventListener('keydown', barcodeKeyListener);
                resolve(keys.join(''));
            });
        });
    }

    FormController.include({
        start: function () {
            const res = this._super.apply(this, arguments);

            // Check if the current model is the target model
            if (this.modelName !== 'ab_inventory_adjust_header') return res

            let F10Pressed = false;
            let keysSent = false;

            this.$el.on('keydown', async function (event) {

                // Handle F10 keypress
                if (event.key === 'F10' && !F10Pressed) {
                    F10Pressed = true;
                    keysSent = false;
                    event.preventDefault(); // Prevent default F10 behavior


                    // Collect barcode keys after F10
                    const barcode = await collectBarcodeKeys();
                    console.log('barcode', barcode);

                    let activeElement = document.activeElement;
                    if (activeElement.tagName === 'INPUT') {
                        console.log('activeElement.tagName', activeElement.tagName)
                        // Simulate Input Action
                        activeElement.value = barcode;
                        activeElement.dispatchEvent(new Event('input', {bubbles: true}));

                        F10Pressed = false; // Reset F10 flag after processing

                        // Wait until dropdown menu fetched
                        const itemsCount = await fetchDropdownItems(barcode)
                        console.log('itemsCount', itemsCount)

                        // If NOT one matching result, DO NOT SEND 'TAB' key
                        if (itemsCount !== 1) return;

                        console.log('Sending Tab Key ...')

                        // send tab key
                        activeElement.dispatchEvent(new KeyboardEvent('keydown', {
                            key: 'Tab',
                            code: 'Tab',
                            keyCode: 9,
                            which: 9,
                            bubbles: true
                        }));
                    }

                }
            });

            return res;
        }
    });
});
