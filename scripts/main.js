(function($) {
  $(function() {
    var mode, showFlags, valuesList, valuesListLength;
    mode = $("body").attr("id");
    // flags
    if (mode == 'batting') {
      showFlags = {'team':true, 'bats':true, 'name':true, 'g':true, 'pa':true, 
                   'ab':true, 'r':true, 'h':true, 'dbl':true, 'tpl':true, 
                   'hr':true, 'tb':true, 'rbi':true, 'sb':true, 'cs':false, 
                   'sh':true, 'sf':true, 'bb':true, 'ibb':false, 'hbp':true, 
                   'so':true, 'gd':true, 'avg':true, 'slg':true, 'obp':true, 
                   'ops':true, 'sbp':false, 'noi':false, 'gpa':false, 
                   'rc':false, 'rc27':false, 'xr':false, 'xr27':false, 
                   'babip':false, 'isop':false, 'isod':false }; 
      valuesList = ['team', 'bats', 'name', 'g', 'pa', 'ab', 'r', 'h', 'dbl', 
                    'tpl', 'hr', 'tb', 'rbi', 'sb', 'cs', 'sbp', 'sh', 'sf', 
                    'bb', 'ibb', 'hbp', 'so', 'gd', 'avg', 'slg', 'obp', 
                    'ops', 'noi', 'gpa', 'rc', 'rc27', 'xr', 'xr27', 'babip', 
                    'isop', 'isod'];
      valuesListLength = valuesList.length;
    } else {
      showFlags = {'team':true, 'throws':true, 'name':true, 'g':true, 'w':true,
                   'l':true, 'sv':true, 'cg':false, 'sho':false, 'zbc':false, 
                   'wpct':true, 'bf':true, 'ip':true, 'h':true, 'hr':true, 
                   'bb':true, 'ibb':false, 'hb':true, 'so':true, 'wp':true, 
                   'bk':true, 'r':true, 'er':true, 'era':true, 'whip':true, 
                   'fip':false, 'lobp':false, 'kbb':false, 'k9':false, 
                   'bb9':false, 'hr9':false, 'ipg':false, 'babip':false};
      valuesList = ['team', 'throws', 'name', 'g', 'w', 'l', 'sv', 'cg', 
                    'sho', 'zbc', 'wpct', 'bf', 'ip', 'h', 'hr', 'bb', 'ibb', 
                    'hb', 'so', 'wp', 'bk', 'r', 'er', 'era', 'whip', 'fip', 
                    'lobp', 'kbb', 'k9', 'bb9', 'hr9', 'ipg', 'babip'];
      valuesListLength = valuesList.length;
    }
    var conv_fullname = {'m': 'marines', 'g': 'giants', 'de': 'baystars',
                         'e': 'eagles', 'f': 'fighters', 's': 'swallows',
                         'l': 'lions', 't': 'tigers', 'bs': 'buffaloes',
                         'h': 'howks', 'd': 'dragons', 'c': 'carp'}
    var loaded_team = [];
    var filter_query = "";
    var base_uri = 'http://' + window.location.host + '/';

    function getReg() {
      var url = base_uri + 'api/?request_kind=games';
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.open("GET", url, false);
      xmlHttp.send(null);
      return $.parseJSON(xmlHttp.responseText);
    }

    var regDic = getReg();

    // data load
    var request_uri = base_uri + 'api/?callback=?';
    function ajaxLoad(team, stats) {
        $.getJSON(request_uri,
                  {'request_kind': 'stats',
                   'team': conv_fullname[team], 
                   'stats_kind': mode},
                 function(data) {
                   var row, cell;
                   for (var i=0; i<data.length; i++) {
                     row = $("<tr></tr>");
                     for (var j=0; j<valuesListLength; j++) {
                       if (showFlags[valuesList[j]] == false) {
                         cell = $("<td></td>")
                           .attr('class', valuesList[j] + ' hide_column')
                           .html(data[i][valuesList[j]]);
                       } else {
                         cell = $("<td></td>")
                           .attr('class', valuesList[j])
                           .html(data[i][valuesList[j]]);
                       }
                       row.append(cell);
                     }
                     $("#maintable tbody").append(row);
                   }
                   $("#maintable").trigger("update");
                   doFilter(filter_query);
                   naColoring();
                 });
    }

    // coloring "N/A"
    function naColoring() {
      $("td").filter(function() {
        return $(this).html() == "-" //|| $(this).html() == "0"
      }).addClass("na");
    }
    
    // show/hide columns
    $("#view_items input").change(function() {
      if ($(this).attr("checked") == "checked") {
        showFlags[$(this).val()] = true;
        $("table ." + $(this).val()).removeClass("hide_column");
      } else {
        showFlags[$(this).val()] = false;
        $("table ." + $(this).val()).addClass("hide_column");
      }
    });
    
    // show/hide teams
    var t, trows;
    $("#view_teams input").change(function() {
      t = $(this).val()
      trows = $("tr").filter(function() {
        return $(this).children(".team").html().toLowerCase() == t;});
      if ($(this).attr("checked") == "checked") {
        if ($.inArray(t, loaded_team) != -1) {
          trows.removeClass("hide_team");
        } else {
          ajaxLoad(t);
          loaded_team.push(t);
        }
      } else {
        trows.addClass("hide_team");
      }
    });

    // show/hide options
    $("#options").outerclick(function() {
      $("#options section.show").removeClass("show");
    });
    $("#options section h1").click(function() {
      if ($(this).parent().hasClass("show")) {
        $("#options section.show").removeClass("show");
      } else {
        $("#options section.show").removeClass("show");
        $(this).parent().addClass("show");
      }
    });
    $("#pa_filter input").focus(function() {
      $("#options .show").removeClass("show");
      $(this).parent().parent().addClass("show");
    });
    $("#pa_filter input").blur(function() {
      $(this).parent().parent().removeClass("show");
    });

    // PA filter
    function canselSubmit(e) {
      if (e.keyCode == 13) {
        if (e.preventDefault) {
          e.preventDefault();
        } else {
          e.returnValue = false;
        }
      }
    }
    function paFilter(query) {
      var method = comp(query);
      var r, team, target, t_full, reg;
      if (mode == 'batting') {
        target = "td.pa";
      } else {
        target = "td.ip";
      }
      if (query.indexOf("r") != -1) {
        $(target).filter(function() {
          team = $(this).parent().children(".team").html()
          t_full = conv_fullname[team.toLowerCase()];
          if (mode == 'batting') {
            reg = Math.round(regDic[t_full] * 2.7);
          } else {
            reg = Math.round(regDic[t_full] * 0.8);
          }
          r = query.replace(/r/, reg);
          r = parseInt(r.match(/[0-9]+/)[0]);
          return !method(r, parseInt($(this).html()));
        }).parent().addClass("hide");
      } else {
        r = parseInt(query.match(/[0-9]+/)[0]);
        $(target).filter(function() {
          return !method(r, parseInt($(this).html()));
        }).parent().addClass("hide");
      }
    }
    function comp(query) {
      if (query.indexOf(">=") == 0) {
        return function(n, m) {return m >= n};
      } else if (query.indexOf("<=") == 0) {
        return function(n, m) {return m <= n};
      } else if (query.indexOf("<") == 0) {
        return function(n, m) {return m < n};
      } else if (query.indexOf(">") == 0) {
        return function(n, m) {return m > n};
      } else {
        return function(n, m) {return m >= n};
      }
    }
    function doFilter(val) {
      if (val.match(/[<>=]*[0-9r]+/)) {
        $("tr.hide").removeClass("hide");
        paFilter(val);
      } else {
        $("tr.hide").removeClass("hide");
      }
      filter_query = val;

      return false
    }
    $("#pa_filter form").submit(function (e){ 
      doFilter($(this).children("input").val());
      return false
    });

    // show/hide placeholder
    var default_value = $("#pa_filter input").val();
    $("#pa_filter input").focus(function(){
      if ($(this).val() == default_value) {
        $(this).val("");
      }
    });
    $("#pa_filter input").blur(function(){
      if ($(this).val() == "") {
        $(this).val(default_value);
      }
    });

    // pinned
    $("#maintable").delegate("td", "click", function() {
      $(this).parent().toggleClass("pinned");
    });
    $("#maintable").delegate("td", "dblclick", function() {
      $(".pinned").removeClass("pinned");
      $(this).parent().addClass("pinned");
    });


    $("#maintable").tablesorter({sortInitialOrder: "desc"});

  });
})(jQuery);
