(function($) {
  $.fn.runOnScope = function(aFunction) {
    $(this).each(function(){
      aFunction.call(this);
    });
  };
})(jQuery);