function createFolders(data,uid) {
    $.each(data.folders, function(index, value){ 
        name = value.substring(value.lastIndexOf('/')+1);
        current = $('li.view_children ul').html();
        link = '<li><a href="/u'+uid + value + '">'+name+'</a></li>';
        $('li.view_children ul').html(current + link);
    });
}

function createMedia(data,uid) {
    $.each(data.images, function(index, value){
        url = 'http://dl.dropbox.com/u/' + uid + value;
        //alert(url);
        img = '<li><a href="'+ url + '"><img src="'+url+'"></img></a></li>\n';
        current = $('section.additional_content ul').html();
        $('section.additional_content ul').html(current + img);
    });
    $.each(data.files, function(index,value){
        url = 'http://dl.dropbox.com/u/' + uid + value;
        name = value.substring(value.lastIndexOf('/')+1);
        //alert(url);
        if (name != '.metadata') {
            img = '<li><a href="'+ url + '">'+name+'</a></li>\n';
            current = $('section.additional_content ul').html();
            $('section.additional_content ul').html(current + img);
        }
    });
}

function metadataCallback(data) {
    if (data.length > 1) {
        url = window.location.pathname;
        var uid = url.substr(2,url.indexOf('/',1)-2);
        var data = jQuery.parseJSON(data);
        createMedia(data,uid);
        createFolders(data,uid);
    }
}

function swapContent(content) {
    var head = "";
    var body = content;
    var contentContainer = $('.text_content');
    if (content.indexOf("~~~~") >= 0) {
        content = content.split("~~~~",2);
        head = content[0].trim();
        body = content[1].trim();
    }
    
    // set header and body content
    $('.subhead_content').html(head);
    contentContainer.html(body);
    // add class to style empty Content area
    if (contentContainer.text().length <= 3) {
      contentContainer.addClass('empty');
      } else { 
          contentContainer.removeClass('empty');
          $.ajax({
              type: 'POST',
              url: window.location.pathname,
              data: 'action=metadata',
              success: metadataCallback
          });
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
    if ($('body').hasClass('public')) {
    }
    getInfo(url);
}

function editCallback(data) {
    var data = jQuery.parseJSON(data);
    if (data.Code == 1) {
        swapContent(data.Message);
    }
}

jQuery(document).ready(function($) {
  var pageLanding = new pageLandingInteractions();
  
  $('body').noisy({
    opacity: 0.07
  });
  
  // show "finish edit" target when editing
  $('.text_content[contenteditable="true"], .subhead_content[contenteditable="true"]').focus(function() {
    $('article').prepend("<div class='finish_edit'>finish edit</div>");
  });
  
  // save content on click out of content editable area
  $('.text_content[contenteditable="true"], .subhead_content[contenteditable="true"]').blur(function() {
      var content = $('.text_content').html().trim();
      if ($('.subhead_content').html() !== "") {
          content = $('.subhead_content').html().trim() + "\n~~~~\n" + content;
      }
      $.ajax({
         type: "POST",
         url: window.location.pathname,
         data: "text=" + escape(content) + "&action=write",
         success: editCallback
      });
      $('.finish_edit').fadeOut(300);
      setTimeout(function(){
        $('.finish_edit').remove();
      }, 300);
  });
  
  // force Content links to go to URL on click instead of edit content
  $('*[contenteditable="true"] a').live('click', function(){
    window.location=$(this).attr('href');
  });
  
  // breadcrumb create page
  var breadcrumbs = $('.breadcrumbs');
  $('input', breadcrumbs).focus(function(){
    $('button', breadcrumbs).show();
  });
  $('input', breadcrumbs).blur(function(){
    setTimeout(function(){
      $('button', breadcrumbs).fadeOut(1000);
    }, 1500);
  });
  $('button', breadcrumbs).click(function(){
    var newPage = $('input', breadcrumbs).val();
    window.location=window.location.pathname+'/'+newPage;
  });
  
});