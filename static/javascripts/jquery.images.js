// create image viewer
var _createImageInterface = function() {
  // hide non-image sections in sidebar
  folders.stop().slideUp(200);
  files.stop().slideUp(200);
  // show images controls
  setTimeout(function(){
    $('.controls', images).slideDown(200);
  }, 200);
  // hide images section title
  $('h1', images).hide();
  // hide article content
  articleContent.hide();
  // create image viewer
  article.prepend(
    '<div class="image_viewer" />'
  );
};

// show image
var _showImage = function(){
  var imageViewer = $('.image_viewer');
  imageViewer.append(
    '<img class="fit_size" src="' + imageSrc + '" />'
  );
  $('img', imageViewer).fadeIn();
};

// Next Image
var _nextImage = function(){
  var nextImage = $('.active', images).next();
  var nextButton = $('.next button', images);
  $('a', nextImage).click();
  nextButton.addClass('highlight');
  setTimeout(function(){
    nextButton.removeClass('highlight');
  }, 200);
};
$('.next:not(.disabled) button', images).click(function(){
    _nextImage();
});
$(document).keydown(function(e) {
  if (e.keyCode == 39) {  // 'Right Arrow' keypress
    _nextImage();
  }
});

// Prev Image
var _prevImage = function(){
  var prevImage = $('.active', images).prev();
  var prevButton = $('.previous button', images);
  $('a', prevImage).click();
  prevButton.addClass('highlight');
  setTimeout(function(){
    prevButton.removeClass('highlight');
  }, 200);
};
$('.previous:not(.disabled) button', images).click(function(){
  _prevImage();
});
$(document).keydown(function(e) {
  if (e.keyCode == 37) {  // 'Left Arrow' keypress
    _prevImage();
  }
});

// close image 
var _closeImage = function(){
  $('.active', images).animate({'width':'29%'}, 150);
  $('li', images).removeClass('active');
  $('.details', images).remove();
  $('.image_viewer img').remove();
};

var _closeImageInterface = function(){
  imageInterfaceOpen = false;
  // close image
  _closeImage();
  // show article content
  articleContent.show();
  // destory image viewer interface
  $('.image_viewer').remove();
  $('.controls', images).hide();
  // restore sidebar lists
  folders.stop().slideDown(300);
  files.stop().slideDown(300);
  $('h1', images).show();
};

// resize_image
$('#size_button, .size_label', images).live('click', function(e){
  var sizeButton = $('#size_button');
  var image = $('.image_viewer img');
  var fitSize = 'fit_size';
  sizeButton.toggleClass('fit_size');
  if(image.attr('class') == fitSize) {
    sizeButton.text('Off');
  } else {
    sizeButton.text('On');
  }
  image.toggleClass(fitSize);
  e.preventDefault();
});

// clicking an active image does: nothing.
$('.active img, .active .image_link', images).live('click', function(e){
  // _closeImage();
  e.preventDefault();
});
// Close image viewer 1) closes the image and 2) shows hidden sections in the sidebar
$('.close', images).click(function(e){
  _closeImageInterface();
  e.preventDefault();
});
$(document).keydown(function(e) {
  if (e.keyCode == 27) {  // 'Escape' keypress
    _closeImageInterface();
  }
});

jQuery(document).ready(function($) {
  imageInterfaceOpen = false;
  // image click
  $('.image_list li:not(.active)').live('click', function(e){
    // is an image already open?
    if (imageInterfaceOpen === true) {
      // destory existing image
      _closeImage();
    } else {
      _createImageInterface();
      imageInterfaceOpen = true;
    }
    // set clicked image as active
    var imageActive = $('img', this);
    imageSrc = imageActive.attr('src');
    var imageTitle = imageActive.closest('a').attr('title');
    $(this).addClass('active').animate({'width':'100%'},150);
    // show active image
    _showImage();
    // create & show image-specific info & controls
    $(this).prepend(
      '<div class="details">' + 
        '<h2>' + imageTitle + '</h2>' +
        '<div class="size_option"><label class="size_label" for="resizer">Fit screen width:</label> <button id="size_button" class="fit_size">On</button></div>' +
        '<a target="_blank" href="' + imageSrc + '">open in new window</a>' +
      '</div>'
    );
    // enable/disable Next and Prev buttons
    var prevImage = $('.active', images).prev();
    var nextImage = $('.active', images).next();
    if(prevImage.length === 0) {
      $('.previous', images).addClass('disabled');
    } else {
      $('.previous', images).removeClass('disabled');
    }
    if(nextImage.length === 0) {
      $('.next', images).addClass('disabled');
    } else {
      $('.next', images).removeClass('disabled');
    }
    e.preventDefault();
  });
});