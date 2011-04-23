(function($) {
  $.fn.defaulted = function() {
    return $(this).each(function() {
      var defaulted = $(this);

      defaulted.addClass('defaulted').focus(function() {
        if ($(this).hasClass('defaulted')) {
          $(this).removeClass('defaulted').val('');
        }
      });

      defaulted.parents('form').submit(function() {
        $('.defaulted', this).val('');
        return true;
      });
    });
  };
})(jQuery);