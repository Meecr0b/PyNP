var pynp_hist = [];

function pynp_init(){
  if (/^auto/i.test($('#po_pynp_width option:selected').text())){
    pynp_graph_autosize();
    $( window ).resize(pynp_graph_autosize);
  }
  
  if (pynp_hist.length > 1){
    var last_hist = pynp_hist.slice(-1)[0];
    $('img.pynp_img').each(function(i, img){
      pynp_graph_reload(img, last_hist[0], last_hist[1]);
    });
    $('.pynp_back').show();
    $('.pynp_back').fadeTo('fast', 1);
  }
  
  $('img.pynp_img').hover(function(){pynp_zoom($( this ));});
  $('.pynp_back').click(function(){
    if (pynp_hist.length > 1){
      pynp_hist.pop();
      var last_hist = pynp_hist.slice(-1)[0];
      $('img.pynp_img').each(function(i, img){
        pynp_graph_reload(img, last_hist[0], last_hist[1]);
      });
    }
    if (pynp_hist.length <= 1 ){
      $('.pynp_back').fadeTo('fast', 0);
      $('.pynp_back').hide();
    }
  });
}

function pynp_graph_autosize(){
  var images = $('img.pynp_img');
  images.hide();
  images.each(function(i, img){
    var closest_td = img.parentNode.parentNode.parentNode;
    img.src = img.src.replace(/([?&]width)=([^#&]*)/, '$1=' + (closest_td.offsetWidth - 120));
    //img.src = img.src.replace(/([?&]width)=([^#&]*)/, '$1=' + ($(this).closest('td')[0].getBoundingClientRect().width - 90));//causes problems with ie8
  });
  images.show();
}

function pynp_graph_reload(img, start, end){
  img.src = img.src.replace(/([?&]start)=([^#&]*)/, '$1=' + start).replace(/([?&]end)=([^#&]*)/, '$1=' + end);

  var date_s = new Date(start*1000);
  var date_e = new Date(end*1000);

  img.title = img.title.replace(/\([\d\.\s:-]*\)/, "(" +
      ("0" + date_s.getDate()).slice(-2) + "." +
      ("0" + date_s.getMonth()).slice(-2) + "." +
      date_s.getFullYear() + " " +
      ("0" + date_s.getHours()).slice(-2) + ":" +
      ("0" + date_s.getMinutes()).slice(-2) + " - " +
      ("0" + date_e.getDate()).slice(-2) + "." +
      ("0" + date_e.getMonth()).slice(-2) + "." +
      date_e.getFullYear() + " " +
      ("0" + date_e.getHours()).slice(-2) + ":" +
      ("0" + date_e.getMinutes()).slice(-2) + ")");
}

function pynp_zoom(img){
  var h = img.height();
  img.imgAreaSelect({
      handles: false,
      minHeight: h,
      maxHeight: h,
      y1: 0,
      y2: h,
      movable: false,
      autoHide: true,
      onSelectEnd: function(img, sel){
          var l = 66;
          var r = 32;
          var w = img.width;

          var img_start = parseInt(/start=(\d+)/.exec(img.src)[1]);
          var img_end = parseInt(/end=(\d+)/.exec(img.src)[1]);
          
          if (pynp_hist.length == 0 ){
            pynp_hist.push([img_start, img_end]);
          }

          var sel_start = parseInt(img_start + ((sel.x1 - l) * (img_end - img_start) / (w - l - r)));
          var sel_end  = parseInt(img_start + ((sel.x2 - l) * (img_end - img_start) / (w - l - r)));
          
          pynp_hist.push([sel_start, sel_end]);

          $('img.pynp_img').each(function(i, img){
            pynp_graph_reload(img, sel_start, sel_end);
          });
      }
  });
  if (pynp_hist.length > 1){
    $('.pynp_back').show();
    $('.pynp_back').fadeTo('fast', 1);
  }
}

// Renders contents for the PyNP hover menus
function pynp_hover_contents(url) {
    return "<table><tr><td><img width=\"300px\" src=\"" + url + "\"></td></tr></table>";
}
