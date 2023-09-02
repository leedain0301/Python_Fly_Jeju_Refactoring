! function(l) {
    "use strict";

    function e() {
        this.$body = l("body"),
            this.$modal = l("#event-modal"),
            this.$calendar = l("#calendar"),
            this.$formEvent = l("#form-event"),
            this.$btnNewEvent = l("#btn-new-event"),
            this.$btnDeleteEvent = l("#btn-delete-event"),
            this.$btnSaveEvent = l("#btn-save-event"),
            this.$modalTitle = l("#modal-title"),
            this.$calendarObj = null,
            this.$selectedEvent = null,
            this.$newEventData = null
    }

    e.prototype.onEventClick = function(e) {
            this.$newEventData = null,
                l("#event-title").val(this.$selectedEvent.title),
                l("#event-category").val(this.$selectedEvent.classNames[0])
        },
        e.prototype.onSelect = function(e) {
            this.$calendarObj.unselect()
        }, e.prototype.init = function() {
            var e = new Date(l.now());


            var t = [],
                a = this;
            a.$calendarObj = new FullCalendar.Calendar(a.$calendar[0], {
                    slotDuration: "00:15:00",
                    slotMinTime: "08:00:00",
                    slotMaxTime: "19:00:00",
                    themeSystem: "bootstrap",
                    bootstrapFontAwesome: !1,
                    buttonText: {
                        today: "Today",
                        month: "Month",
                        prev: "< Prev",
                        next: "Next >"
                    },
                    initialView: "dayGridMonth",
                    handleWindowResize: !0,
                    height: l(window).height() - 200,
                    headerToolbar: {
                        left: "prev,next today",
                        center: "title",
                        right: "dayGridMonth"
                    },

                    initialEvents: function(info, successCallback, failureCallback) {
                        var defaultEvents = [];
                        var $this = this;
                        $.ajax({
                            url: '/demo',
                            method: 'GET',
                            dataType: 'json',
                            success: function(data) {
                                var airplane = JSON.parse(data);
                                jQuery.each(airplane, function() {
                                    var colorinput = "#FFDFDF";
                                    switch (this.rankingbyweek) {
                                        case 1:
                                            colorinput = "#FF5B5B";
                                            break;
                                        case 2:
                                            colorinput = "#FF7373";
                                            break;
                                        case 3:
                                            colorinput = "#FF8787";
                                            break;
                                        case 4:
                                            colorinput = "#FFA1A1";
                                            break;
                                        case 5:
                                            colorinput = "#FFBBBB";
                                            break;
                                        case 6:
                                            colorinput = "#FFDFDF";
                                            break;
                                        default:
                                            colorinput = "#FFDFDF";
                                            break;
                                    }
                                    defaultEvents.push({
                                        title: Number(this.mincharge).toLocaleString() + "원",
                                        start: dateformat(this.date),
                                        color: colorinput
                                    });
                                });
                                successCallback(defaultEvents);
                                // console.log("defaultEvents", defaultEvents);
                            },
                            error: function() {
                                // 데이터를 가져오는 도중 에러가 발생한 경우 실행되는 콜백 함수
                                console.log('Failed to fetch events data.');
                            }
                        });
                    },
                    editable: false,
                    droppable: false,
                    selectable: false,
                    dateClick: function(e) {
                        var clickedDate = e.dateStr;
                        window.location.href = "http://localhost:9999/filghtDate?selectedDate=" + clickedDate + "&statusselect2=GMP&statusselect1=0"
                    },
                    eventClick: function(e) {
                        var clickedEvent = dateformat(e.event.start);
                        window.location.href = "http://localhost:9999/filghtDate?selectedDate=" + clickedEvent + "&statusselect2=GMP&statusselect1=0"
                    }
                }),
                // 캘린더로 데이터 전달
                a.$calendarObj.render()
        },
        l.CalendarApp = new e,
        l.CalendarApp.Constructor = e

    function dateformat(date_str) {
        var date = new Date(date_str);
        var year = date.getFullYear();
        var month = ("0" + (date.getMonth() + 1)).slice(-2);
        var day = ("0" + date.getDate()).slice(-2);
        var formatted_date = year + "-" + month + "-" + day;
        return formatted_date;
    }
}(window.jQuery),
function() {
    "use strict";
    window.jQuery.CalendarApp.init()
}();