
// only 2 of investment strategies selected validation
$("#invest-form input[type='checkbox']").change(function(e) {
    if (e.target.checked) {
        if ($("#invest-form input[type='checkbox']:checked").length > 2) {
           alert("You can only select up to 2 investment strategies!");
           e.target.checked=false;
        }
    } 
});
// input textfield, only digits are allowed
$("#invest-form input[name='amount']").on('keyup', function(e) {
    var curValue = e.target.value;
    var replaced = "";
    for(var i = 0; i < curValue.length; i++) {
        if (curValue[i] >= '0' && curValue[i] <= '9') {
            replaced = replaced + curValue[i];
        } 
    }
    e.target.value = replaced;
 });

 // make investment strategies chatboxes array as hidden input
 function investFormOnsubmit(e) {
    
    var form = $(e.target);
    var stratsStr = "";
    var amount = form.find("input[name='amount']")[0].value;
    if(amount == "" || parseInt(amount) < 5000) {
        alert("You should input an amount which is at least $5,000!")
        e.preventDefault();
        return false;
    }
    if (form.find("input[type='checkbox']:checked").length == 0) {
        alert("You should at least pick one investment strategy!");
        e.preventDefault();
        return false;
    }
    form.find("input[type='checkbox']:checked").each(function() {
        stratsStr += (stratsStr ? "," : "");
        stratsStr += ($(this).attr('name'));
    });
    form.append("<input type='hidden' name='strats' value='" + stratsStr +"'>")
    return true;
 }