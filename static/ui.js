// --------------------- Common Functions -----------------------------------

function initPage(){
    $('body').on('mousedown', 'div', function(e) {
        if($(this).hasClass('bm-draggable')) {
            $("body").css("cursor", "move");
            var target = $("#" + $(this).attr("target-bind"));
            var offsety = e.pageY - $(target).position().top;
            var offsetx = e.pageX - $(target).position().left;
            $(target).addClass('draggable').parents().on('mousemove', function(e) {
                $('.draggable').offset({
                    top: e.pageY - offsety,
                    left: e.pageX - offsetx
                }).on('mouseup', function(){
                    $(target).removeClass('draggable');
                });
                e.preventDefault();
            });
        }
    }).on('mouseup', function() {
        $('.draggable').removeClass('draggable');
        $("body").css("cursor", "auto");
    });
};

