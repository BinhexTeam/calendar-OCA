/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ResourceBookingCreate = publicWidget.Widget.extend({
    selector: "#wrapwrap:has(.new_booking_form)",
    events: {
        "click .new_booking_confirm": "_onNewBookingConfirm",
    },

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
    },

    // --------------------------------------------------------------------------
    // Private
    // --------------------------------------------------------------------------

    /**
     * @private
     * @param {jQuery} $btn
     * @param {function} callback
     * @returns {Promise}
     */
    _buttonExec: function ($btn, callback) {
        // TODO remove once the automatic system which does this lands in master
        $btn.prop("disabled", true);
        return callback.call(this).catch(function (e) {
            $btn.prop("disabled", false);
            if (e instanceof Error) {
                return Promise.reject(e);
            }
        });
    },
    /**
     * @private
     * @returns {Promise}
     */
    _createBooking: function () {
        return this.orm
            .call("resource.booking", "create_booking_portal", [
                {
                    resource_name: $(".new_booking_form .resource_name").val(),
                    resource_type: $(".new_booking_form .resource_type").val(),
                    description: $(".new_booking_form .resource_description").val(),
                },
            ])
            .then(function (response) {
                if (response.errors) {
                    $("#new-booking-dialog .alert").remove();
                    $("#new-booking-dialog div:first").prepend(
                        '<div class="alert alert-danger">' + response.errors + "</div>"
                    );
                    return Promise.reject(response);
                }
                window.location = `/my/bookings/${response.id}/schedule`;
            });
    },

    // --------------------------------------------------------------------------
    // Handlers
    // --------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onNewBookingConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createBooking);
    },
});
