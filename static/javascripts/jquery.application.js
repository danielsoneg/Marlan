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
    console.log(content);
    content = content.content;
    var head = "";
    var body = content;
    if (content.indexOf("~~~~") >= 0) {
        content = content.split("~~~~",2);
        head = content[0].trim();
        body = content[1].trim();
    }
    
    // set header and body content
    var articleFadeIn = 400;
    articleSubhead.html(head).fadeIn(articleFadeIn);
    articleText.html(body).fadeIn(articleFadeIn);
    
    // empty Subhead
    if (articleSubhead.text().length < 1) {
      articleSubhead.addClass('empty');
      articleSubhead.blur(function(){
        if ($(this).text().length > 0) {
          $(this).removeClass('empty');
        }
      });
    } else { 
      articleSubhead.removeClass('empty');
    }
    // empty Content
    if (articleText.text().length < 1) {
      articleText.addClass('empty');
    } else { 
      articleText.removeClass('empty');
    }
    // estimate reading time
    var wordCount = ($('.text_content', article).text().length / 5);
    var minutes = +(wordCount / 200).toFixed(0);
    var seconds = +(wordCount % 200 / (200/60)).toFixed(0);
    if(minutes >= 1) {
      $('.reading_time', article).html('Estimated reading time: <strong>' + minutes + ' minute(s) ' + seconds + ' seconds.</strong>').fadeIn(articleFadeIn);
    } else {
      $('.reading_time').fadeOut();
    }
    return;
};

var _getInfo = function(url) {
    $.ajax({
       type: "GET",
       url: url,
       dataType: 'json',
       success: _swapContent
    });
    return;
};

function pageLandingInteractions(){
    var url = window.location.pathname;
    if (!url.match(".txt$")) {
        url = url + '/info.txt';
    }
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

// breadcrumb "parent" button to up one level
var _breadcrumbParent = function(){
  var parent = $('.current', nav).prev();
  var parentUrl = $('a', parent).attr('href');
  $('.parent a', nav).attr('href',parentUrl);
  $('.parent a').click(function(){
    $('a', parent).addClass('highlight');
  });
};

var _contentEditing = function(){
  // show Finish Editing button when editing
  contentEditable.focus(function() {
    $('.reading_time', article).hide();
    $(article).prepend('<div class="finish_editing" tabindex="2">Finish Editing</div>');
    // Finish editing if hit "escape" key
    $(document).keydown(function(e) {
      if (e.keyCode == 27) { // "Escape""
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
};

var _passwordToggle = function(){
  passwordInterface.toggleClass('active');
  $('body').toggleClass('overlay');
};
// Password Interface
var _passwordInterface = function(){
  passwordInterface = $('.password', nav);
  $('span', passwordInterface).click(function(){
    _passwordToggle();
  });
};

// show sidebar files list instructional text
$('.info', aside).click(function(){
  $(this).toggleClass('active');
});

// force Content links to go to URL on click instead of edit content
$('a', contentEditable).live('click', function(){
  window.location=$(this).attr('href');
});

jQuery(document).ready(function($) {
  var pageLanding = new pageLandingInteractions();
  
  // expand content width if no asides
  if((aside).length === 0) {
    article.css({'left':'0'});
  }
  
  // Immediately hide page content so that it can have a pretty .fadeIn on page load (see _swapContent). This .hide goes in doc.ready so it's only hiding-and-fading on page load, instead of every time you make changes to the text.
  contentEditable.hide();
  
  _breadcrumbParent();
  _contentEditing();
  _passwordInterface();
  
  // jquery.defaulted init
  $('input.defaulted, textarea.defaulted').defaulted();
});