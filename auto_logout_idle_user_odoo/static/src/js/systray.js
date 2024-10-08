/** @odoo-module **/
import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';
import rpc from 'web.rpc';

const WARNING_LIMIT = 50000;
const WARNING_CLASS = ['text-danger', 'bg-light', 'border', 'border-danger', 'rounded'];
var ajax = require('web.ajax');
var TimerWidget = Widget.extend({
    template: 'TimerSystray',
    /**
     function run before loading the page to call methode "get_idle_time"
     */
    willStart: function () {
        var self = this;
        return this._super().then(function () {
            self.get_idle_time();
        });
    },
    /**
     Getting minutes through python for the corresponding user in the backend
     */
    get_idle_time: function () {
        var self = this
        var now = new Date().getTime();

        ajax.rpc('/get_idle_time/timer', {}).then(function (data) {
            if (data !== false) {
                self.minutes = data;
                self.idle_timer();

            }
        })
    },
    /**
     passing values of the countdown to the xml
     */
    idle_timer: function () {
        var nowt = new Date().getTime();
        var date = new Date(nowt);
        var self = this;
        date.setMinutes(date.getMinutes() + this.minutes);
        var updatedTimestamp = date.getTime();

        /** Running the count down using setInterval function */
        var idle = setInterval(function () {
            var now = new Date().getTime();
            var distance = updatedTimestamp - now;
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            if (hours && days) {
                self.el.querySelector("#idle_timer").innerHTML = "<i class='fa fa-clock-o systray-icon' /> " + days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
            } else if (hours) {
                self.el.querySelector("#idle_timer").innerHTML = "<i class='fa fa-clock-o systray-icon' /> " + hours + "h " + minutes + "m " + seconds + "s ";
            } else {
                self.el.querySelector("#idle_timer").innerHTML = "<i class='fa fa-clock-o systray-icon' /> " + minutes + "m " + seconds + "s ";
            }
            if (distance <= WARNING_LIMIT) {
                /** if the countdown is near zero  the timer will be red*/
                self.el.querySelector("#idle_timer").classList.add(...WARNING_CLASS);

                /** if the countdown reaches zero, run python end session function */
                if (distance < 0) {
                    clearInterval(idle);
                    self.el.querySelector("#idle_timer").innerHTML = "EXPIRED";
                    // bad way to end session
                    // location.replace("/web/session/logout")
                    return rpc.query({
                        model: 'res.users',
                        method: 'auth_timeout_session_terminate',
                    });
                }
            } else if (self.el.querySelector("#idle_timer").classList.contains(...WARNING_CLASS)) {
                self.el.querySelector("#idle_timer").classList.remove(...WARNING_CLASS);
            }
        }, 1000);

        /**
         * Reset the idle time
         */
        function resetTimer() {
            var nowt = new Date().getTime();
            var date = new Date(nowt);
            date.setMinutes(date.getMinutes() + self.minutes);
            updatedTimestamp = date.getTime();
        }

        /**
         * Calling the resetTimer() for each event
         */
        const events = ['mousemove', 'keypress', 'click', 'touchstart', 'mousedown', 'load'];
        for (const event of events) {
            document.addEventListener(event, resetTimer);
        }
    },
});
SystrayMenu.Items.push(TimerWidget);

export default TimerWidget;