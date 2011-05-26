(function($) {
  $.fn.defaulted = function() {
    return $(this).each(function() {
      var defaulted = $(this);
      var defaultedValue = $(this).val();
      defaulted.addClass('defaulted').focus(function() {
        if ($(this).hasClass('defaulted')) {
          $(this).removeClass('defaulted').val('');
        }
      });
      defaulted.blur(function(){
        if ($(this).val().length === 0) {
          $(this).val(defaultedValue);
        }
      });

      defaulted.parents('form').submit(function() {
        $('.defaulted', this).val('');
        return true;
      });
    });
  };
})(jQuery);