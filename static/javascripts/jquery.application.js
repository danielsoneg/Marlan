function createFolders(data,uid) {
    if (data.folders.length > 0) {
        var asideContents = "<ol class='folders'>";
        $.each(data.folders, function(index, value){ 
            name = value.substring(value.lastIndexOf('/')+1);
            link = "\n<li><a href='/u"+uid + value + "'>"+name+'</a></li>';
            asideContents = asideContents + link;
        });
        asideContents = asideContents + "\n</ul>";
        aside.html(asideContents);
    }
}

function createMedia(data,uid) {
    var asideContents = aside.html();
    if (data.files.length > 0) {
        asideContents = asideContents + '\n<ul class="files">';
        $.each(data.files, function(index,value){
            url = 'http://dl.dropbox.com/u/' + uid + value;
            name = value.substring(value.lastIndexOf('/')+1);
            //alert(url);
            link = '<li><a href="'+ url + '">'+name+'</a></li>\n';
            asideContents = asideContents + link;
        });
        asideContents = asideContents + '\n</ul>';
    }
    if (data.images.length > 0) {
        asideContents = asideContents + '\n<ul class="images">';
        $.each(data.images, function(index, value){
            url = 'http://dl.dropbox.com/u/' + uid + value;
            //alert(url);
            img = '<li><a href="'+ url + '"><img src="'+url+'"></img></a></li>\n';
            asideContents = asideContents + img;
        });
        asideContents = asideContents + "\n</ul>";
    }
    aside.html(asideContents);
}

function passCallback(data) {
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: 'action=metadata',
        success: metadataCallback
    });
}

function metadataCallback(data) {
    if (data === 0) {
        //Incorrect Password Stuff Goes Here
        alert('Wrong Pass!');
    }
    if (data.length > 1) {
        url = window.location.pathname;
        var uid = url.substr(2,url.indexOf('/',1)-2);
        data = jQuery.parseJSON(data);
        createFolders(data,uid);
        createMedia(data,uid);
        if ($('body').hasClass('public')) {
            var url = window.location.pathname +'/info.txt';
            getInfo(url);
        }
    }        
}

function swapContent(content) {
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
          if ($('body').hasClass('private')){
              $.ajax({
                  type: 'POST',
                  url: window.location.pathname,
                  data: 'action=metadata',
                  success: metadataCallback
              });
          }
    }
    // estimate reading time
    var wordCount = ($('.text_content', article).text().length / 5);
    var minutes = (wordCount / 200).toFixed(0);
    var seconds = (wordCount % 200 / (200/60)).toFixed(0);
    if((wordCount / 200) >= 1) {
      setTimeout(function(){
        $('.reading_time', article).fadeIn(2000).html('Estimated reading time: <strong>' + minutes + ' minute(s) ' + seconds + ' seconds.</strong>');
      }, 150);
    } else {
      $('.reading_time').fadeOut(700);
    }
    return;
}

function getInfo(url) {
    $.ajax({
       type: "GET",
       url: url,
       success: swapContent
    });
    return;
}

function pageLandingInteractions(){
    var url = window.location.pathname +'/info.txt';
    if (!$('body').hasClass('public')) {
        getInfo(url);
    }
}

function editCallback(data) {
    var data = jQuery.parseJSON(data);
    if (data.Code == 1) {
        swapContent(data.Message);
    }
}

jQuery(document).ready(function($) {
  var pageLanding = new pageLandingInteractions();
  article = $('article');
  articleContent = $('.content', article);
  articleHeader = $('.article_header', article);
  articleSubhead = $('h2', articleHeader);
  articleText = $('.text_content', article);
  contentEditable = $('*[contenteditable="true"]', article);
  nav = $('body > nav');
  aside = $('aside', article);
  
  if ($('li.item', nav).length < 2) {
    $('.parent', nav).hide();
  }
  // breadcrumb go up one level
  var parent = $('.current', nav).prev();
  var parentUrl = $('a', parent).attr('href');
  $('.parent a', nav).attr('href',parentUrl);
  
  // expand content width if no asides
  if((aside).length === 0) {
    article.css({'left':'0'});
  }

  contentEditable.hide();
  contentEditable.focus(function() {
    $('.reading_time', article).hide();
    $(article).prepend('<div class="finish_editing" tabindex="2">Finish Editing</div>');
  });
  // save content on click out of content editable area
  contentEditable.blur(function() {
    $('.finish_editing').fadeOut(300);
    var content = articleText.html().trim();
    if (articleSubhead.html() !== "") {
      content = articleSubhead.html().trim() + "\n~~~~\n" + content;
    }
    $.ajax({
     type: "POST",
     url: window.location.pathname,
     data: "text=" + escape(content) + "&action=write",
     success: editCallback
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
  $('#pwgo').click(function(){
    var pass = '' + $('#pw').val();
    $.ajax({
      type: "POST",
      url: window.location.pathname,
      data: "pw=" + escape(pass) + "&action=public",
      success: passCallback
    });
  });
  $('#pubgo').click(function(){
      var pass = '' + $('#pw').val();
      $.ajax({
          type: 'POST',
          url: window.location.pathname,
          data: "pw=" + escape(pass) + '&action=metadata',
          success: metadataCallback
      });
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
    $('input', createPage).stop().removeClass('active').animate({'width':createPageWidth}, 200);
    $('button', createPage).fadeOut(50);
  });
  
  // show files info
  var info = $('.info', aside);
  info.click(function(){
    info.toggleClass('active');
  });
  
  // image click
  var images = $('.images', aside);
  $('li:not(.active)', images).live('click', function(e){
    _closeImage();

    var imageSrc = $('img', this).attr('src');
    var imageTitle = $('img', this).closest('a').attr('title');
    $(this).addClass('active');
    articleContent.hide();
    $('.image_viewer').remove();
    article.prepend(
      '<div class="image_viewer">' +
        '<ul>' +
          '<li class="title">' + imageTitle + '</li>' +
          '<li class="close action">close image</li>' +
          '<li class="direct action"><a href="' + imageSrc + '">direct link to image</a></li>' +
          '<li class="size action"><a href="#">view original size</a></li>' +
        '</ul>' +
        '<img src="' + imageSrc + '" />' +
      '</div>'
    );
    $('.image_viewer img').fadeIn();
    e.preventDefault();
  });

  // resize_image
  $('.image_viewer .size a').live('click', function(e){
    var image = $('.image_viewer img');
    var fullSize = 'full_size';
    if(image.attr('class') == fullSize) {
      $('.image_viewer .size a').text('view original size');
    } else {
      $('.image_viewer .size a').text('fit to screen');
    }
    image.toggleClass(fullSize);
    e.preventDefault();
  });

  // close image 
  var _closeImage = function(){
    $('li', images).removeClass('active');
    $('.image_viewer').remove();
    articleContent.show();
  };
  $('.active', images).live('click', function(e){
    _closeImage();
    e.preventDefault();
  });
  $('.image_viewer .close').live('click', function(e){
    _closeImage();
    e.preventDefault();
  });
});