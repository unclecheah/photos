function breadcrumbs (fpath) {
    tokens = ["Home"]
    if (fpath) tokens = tokens.concat (fpath.split ("/"));
    $('.breadcrumb-item').remove ();

    alink = '';
    for (token in tokens) {
        if (token != 0) {
            if (alink == '') alink = tokens[token];
            else alink += '/' + tokens[token];
        }

        console.log (token);
        console.log (tokens.length);
        href = "href='" + (token == 0 ? "/" : '?d=' + alink) + "'";
        if (token == tokens.length - 1) href += " style='pointer-events: none;'";

        ht = "  <li class='breadcrumb-item'>"
            + "     <a class='link-body-emphasis fw-semibold text-decoration-none' " + href + ">"
            + (token == 0? "<svg class='bi' width='16' height='16'><use xlink:href='#house-door-fill'></use></svg>" : "")
            + tokens[token]
            + "     </a>"
            + " </li>";

        $(".breadcrumb").append (ht);
    }

};

function loadingComplete () {
    var params = new URLSearchParams (window.location.search)
    breadcrumbs (params.get ('d'));
    $.LoadingOverlay ('hide');
};
