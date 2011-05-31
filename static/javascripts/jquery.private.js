var writeMetadata = function() {
  $.ajax({
    type: 'POST',
    url: window.location.pathname,
    data: 'action=metadata'
  });
};

// set password for sharing
var shareSet = function() {
  _passwordToggle();
  //writeMetadata();
  return;
};
$('#pwgo').click(function(){
  var pass = $('#pw').val();
  $.ajax({
    type: "POST",
    url: window.location.pathname,
    data: "pw=" + escape(pass) + "&action=share",
    success: shareSet
  });
  return false;
});

// create child directory
var _createChildDirectory = function(){
  var createPage = $('.create_page', nav);
  var createPageWidth = $('input', createPage).width();
  $('button', createPage).click(function(){
    var newPage = $('input', createPage).val();
    window.location=window.location.pathname+'/'+newPage;
  });
  $('input', createPage).focus(function(){
    $('input', createPage).stop().addClass('active').animate({'width':'150px'}, 200);
    setTimeout(function(){
      $('button', createPage).fadeIn(50);
    }, 150);
  });
  $('input', createPage).blur(function(){
    setTimeout(function(){
      $('input', createPage).stop().removeClass('active').animate({'width':createPageWidth}, 200);
      $('button', createPage).fadeOut(50);      
    }, 2000);
  });

};

jQuery(document).ready(function($) {
  _createChildDirectory();
});