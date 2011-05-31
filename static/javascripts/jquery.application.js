article = $('article');
articleContent = $('.content', article);
articleHeader = $('.article_header', article);
articleSubhead = $('h2', articleHeader);
articleText = $('.text_content', article);
contentEditable = $('*[contenteditable="true"]', article);
nav = $('body > nav');
aside = $('aside', article);
folders = $('.folders', aside);
images = $('.images', aside);
files = $('.files', aside);

//Need this everywhere
_swapContent = function(content) {
    var head = "";
    var body = content;
    if (content.indexOf("~~~~") >= 0) {
        content = content.split("~~~~",2);
        head = content[0].trim();
        body = content[1].trim();
    }
    
    // set header and body content
    articleSubhead.html(head).fadeIn(150);
    articleText.html(body).fadeIn(150);
    // add class to style empty Content area
    if (articleText.text().length <= 3) {
      articleText.addClass('empty');
      } else { 
          articleText.removeClass('empty');
    }
    // estimate reading time
    var wordCount = ($('.text_content', article).text().length / 5);
    var minutes = +(wordCount / 200).toFixed(0);
    var seconds = +(wordCount % 200 / (200/60)).toFixed(0);
    if(minutes >= 1) {
      $('.reading_time', article).fadeIn(1400).html('Estimated reading time: <strong>' + minutes + ' minute(s) ' + seconds + ' seconds.</strong>');
    } else {
      $('.reading_time').fadeOut();
    }
    return;
};

var _getInfo = function(url) {
    $.ajax({
       type: "GET",
       url: url,
       success: _swapContent
    });
    return;
};

function pageLandingInteractions(){
    var url = window.location.pathname +'/info.txt';
    if (!$('body').hasClass('public')) {
        _getInfo(url);
    }
}

var _editCallback = function(data) {
    var editCallbackData = jQuery.parseJSON(data);
    if (editCallbackData.Code === 1) {
        _swapContent(editCallbackData.Message);
    }
};

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
  // 'Right Arrow' keypress
  if (e.keyCode == 39) {
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
  // 'Left Arrow' keypress
  if (e.keyCode == 37) {
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
  // 'Escape' keypress
  if (e.keyCode == 27) {
    _closeImageInterface();
  }
});

jQuery(document).ready(function($) {
  var pageLanding = new pageLandingInteractions();
  
  // breadcrumb go up one level
  var parent = $('.current', nav).prev();
  var parentUrl = $('a', parent).attr('href');
  $('.parent a', nav).attr('href',parentUrl);
  $('.parent a').click(function(){
    $('a', parent).addClass('highlight');
  });
  
  // expand content width if no asides
  if((aside).length === 0) {
    article.css({'left':'0'});
  }

  // paired with a fadeIn above, .hide() prevents a flash on content save
  contentEditable.hide();
  
  // show Finish Editing button when editing
  contentEditable.focus(function() {
    $('.reading_time', article).hide();
    $(article).prepend('<div class="finish_editing" tabindex="2">Finish Editing</div>');
    $(document).keydown(function(e) {
      // Escape keypress
      if (e.keyCode == 27) {
        contentEditable.blur();
      }
    });
  });

  // save content on click out of content editable area
  contentEditable.blur(function() {
    // hide Finish Editing button
    $('.finish_editing').remove();
    // save content
    var content = articleText.html().trim();
    if (articleSubhead.html() !== "") {
      content = articleSubhead.html().trim() + "\n~~~~\n" + content;
    }
    $.ajax({
     type: "POST",
     url: window.location.pathname,
     data: "text=" + escape(content) + "&action=write",
     success: _editCallback
    });
  });
  
  // force Content links to go to URL on click instead of edit content
  $('a', contentEditable).live('click', function(){
    window.location=$(this).attr('href');
  });
  
  // security
  var security = $('.security', nav);
  $('span', security).click(function(){
    security.toggleClass('active');
    $('body').toggleClass('overlay');
  });
  
  // create page
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
  
  // show sidebar files list instructional text
  var info = $('.info', aside);
  info.click(function(){
    info.toggleClass('active');
  });
  
  // image click
  imageInterfaceOpen = false;
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

  // jquery.defaulted init
  $('input.defaulted, textarea.defaulted').defaulted();
});