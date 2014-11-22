$(document).ready() { function() {
    function validate() { 
        ...
    }

    var oldOnClick = $("input[value=OK]").attr("onclick");
    $("input[value=OK]").attr("onclick", "if(!validate()) { return false; }" + oldOnClick));
});