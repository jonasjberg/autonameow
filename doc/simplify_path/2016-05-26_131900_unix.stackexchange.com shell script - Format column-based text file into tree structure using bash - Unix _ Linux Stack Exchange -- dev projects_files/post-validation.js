StackExchange.postValidation=function(){function e(e,t,n,a){var i=e.find('input[type="submit"]:visible'),o=i.length&&i.is(":enabled");o&&i.attr("disabled",!0),r(e,a),s(e,t,n,a),l(e),u(e),d(e);var p=function(){1!=t||e.find(E).length?(c(e,a),o&&i.attr("disabled",!1)):setTimeout(p,250)};p()}function t(t,a,r,s,c){e(t,a,s,r);var l,u=function(e){if(e.success)if(c)c(e);else{var n=window.location.href.split("#")[0],i=e.redirectTo.split("#")[0];0==i.indexOf("/")&&(i=window.location.protocol+"//"+window.location.hostname+i),l=!0,window.location=e.redirectTo,n.toLowerCase()==i.toLowerCase()&&window.location.reload(!0)}else e.captchaHtml?e.nocaptcha?StackExchange.nocaptcha.init(e.captchaHtml,u):StackExchange.captcha.init(e.captchaHtml,u):e.errors?(t.find("input[name=priorAttemptCount]").val(function(e,t){return(+t+1||0).toString()}),h(e.errors,t,a,r,e.warnings)):t.find('input[type="submit"]:visible').parent().showErrorMessage(e.message)};t.submit(function(){if(t.find("#answer-from-ask").is(":checked"))return!0;var e=t.find(C);if("[Edit removed during grace period]"==$.trim(e.val()))return m(e,["Comment reserved for system use. Please use an appropriate comment."],p()),!1;o(),StackExchange.navPrevention&&StackExchange.navPrevention.stop();var a=t.find('input[type="submit"]:visible');if(a.parent().addSpinner(),StackExchange.helpers.disableSubmitButton(t),StackExchange.options.site.enableNewTagCreationWarning){var s=t.find(E).parent().find("input#tagnames"),c=s.prop("defaultValue");if(s.val()!==c)return $.ajax({"type":"GET","url":"/posts/new-tags-warning","dataType":"json","data":{"tags":s.val()},"success":function(e){e.showWarning?a.loadPopup({"html":e.html,"dontShow":!0,"prepend":!0,"loaded":function(e){n(e,t,l,r,u)}}):i(t,r,l,u)}}),!1}return setTimeout(function(){i(t,r,l,u)},0),!1})}function n(e,t,n,o,r){e.bind("popupClose",function(){a(t,n)}),e.find(".submit-post").click(function(a){return StackExchange.helpers.closePopups(e),i(t,o,n,r),a.preventDefault(),!1}),e.show()}function a(e,t){StackExchange.helpers.removeSpinner(),t||StackExchange.helpers.enableSubmitButton(e)}function i(e,t,n,i){$.ajax({"type":"POST","dataType":"json","data":e.serialize(),"url":e.attr("action"),"success":i,"error":function(){var n;switch(t){case"question":n="An error occurred submitting the question.";break;case"answer":n="An error occurred submitting the answer.";break;case"edit":n="An error occurred submitting the edit.";break;case"tags":n="An error occurred submitting the tags.";break;case"post":default:n="An error occurred submitting the post."}e.find('input[type="submit"]:visible').parent().showErrorMessage(n)},"complete":function(){a(e,n)}})}function o(){for(var e=0;e<M.length;e++)clearTimeout(M[e]);M=[]}function r(e,t){var n=e.find(y);n.length&&n.blur(function(){M.push(setTimeout(function(){var a=n.val(),i=$.trim(a);if(0==i.length)return k(e,n),void 0;var o=n.data("min-length");if(o&&i.length<o)return m(n,[function(e){return 1==e.minLength?"Title must be at least "+e.minLength+" character.":"Title must be at least "+e.minLength+" characters."}({"minLength":o})],p()),void 0;var r=n.data("max-length");return r&&i.length>r?(m(n,[function(e){return 1==e.maxLength?"Title cannot be longer than "+e.maxLength+" character.":"Title cannot be longer than "+e.maxLength+" characters."}({"maxLength":r})],p()),void 0):($.ajax({"type":"POST","url":"/posts/validate-title","data":{"title":a},"success":function(a){a.success?k(e,n):m(n,a.errors.Title,p()),"edit"!=t&&g(e,n,a.warnings.Title)},"error":function(){k(e,n)}}),void 0)},A))})}function s(e,t,n,a){var i=e.find(S);i.length&&i.blur(function(){M.push(setTimeout(function(){var o=i.val(),r=$.trim(o);if(0==r.length)return k(e,i),void 0;if(5==t){var s=i.data("min-length");return s&&r.length<s?m(i,[function(e){return"Wiki Body must be at least "+e.minLength+" characters. You entered "+e.actual+"."}({"minLength":s,"actual":r.length})],p()):k(e,i),void 0}(1==t||2==t)&&$.ajax({"type":"POST","url":"/posts/validate-body","data":{"body":o,"oldBody":i.prop("defaultValue"),"isQuestion":1==t,"isSuggestedEdit":n},"success":function(t){t.success?k(e,i):m(i,t.errors.Body,p()),"edit"!=a&&g(e,i,t.warnings.Body)},"error":function(){k(e,i)}})},A))})}function c(e,t){var n=e.find(E);if(n.length){var a=n.parent().find("input#tagnames");a.blur(function(){M.push(setTimeout(function(){var i=a.val(),o=$.trim(i);return 0==o.length?(k(e,n),void 0):($.ajax({"type":"POST","url":"/posts/validate-tags","data":{"tags":i,"oldTags":a.prop("defaultValue")},"success":function(a){if(a.success?k(e,n):m(n,a.errors.Tags,p()),"edit"!=t&&(g(e,n,a.warnings.Tags),a.source&&a.source.Tags&&a.source.Tags.length)){var i=$("#post-form input[name='warntags']");i&&StackExchange.using("gps",function(){var e=i.val()||"";$.each(a.source.Tags,function(t,n){n&&!i.data("tag-"+n)&&(i.data("tag-"+n,n),e=e.length?e+" "+n:n,StackExchange.gps.track("tag_warning.show",{"tag":n},!0))}),i.val(e),StackExchange.gps.sendPending()})}},"error":function(){k(e,n)}}),void 0)},A))})}}function l(e){var t=e.find(C);t.length&&t.blur(function(){M.push(setTimeout(function(){var n=t.val(),a=$.trim(n);if(0==a.length)return k(e,t),void 0;var i=t.data("min-length");if(i&&a.length<i)return m(t,[function(e){return 1==e.minLength?"Your edit summary must be at least "+e.minLength+" character.":"Your edit summary must be at least "+e.minLength+" characters."}({"minLength":i})],p()),void 0;var o=t.data("max-length");return o&&a.length>o?(m(t,[function(e){return 1==e.maxLength?"Your edit summary cannot be longer than "+e.maxLength+" character.":"Your edit summary cannot be longer than "+e.maxLength+" characters."}({"maxLength":o})],p()),void 0):(k(e,t),void 0)},A))})}function u(e){var t=e.find(T);t.length&&t.blur(function(){M.push(setTimeout(function(){var n=t.val(),a=$.trim(n);if(0==a.length)return k(e,t),void 0;var i=t.data("min-length");if(i&&a.length<i)return m(t,[function(e){return"Wiki Excerpt must be at least "+e.minLength+" characters; you entered "+e.actual+"."}({"minLength":i,"actual":a.length})],p()),void 0;var o=t.data("max-length");return o&&a.length>o?(m(t,[function(e){return"Wiki Excerpt cannot be longer than "+e.maxLength+" characters; you entered "+e.actual+"."}({"maxLength":o,"actual":a.length})],p()),void 0):(k(e,t),void 0)},A))})}function d(e){var t=e.find(I);t.length&&t.blur(function(){M.push(setTimeout(function(){var n=t.val(),a=$.trim(n);return 0==a.length?(k(e,t),void 0):/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,20}$/i.test(n)?(k(e,t),void 0):(m(t,["This email does not appear to be valid."],f()),void 0)},A))})}function p(){var e=$("#sidebar, .sidebar").first().width()||270;return{"position":{"my":"left top","at":"right center"},"css":{"max-width":e,"min-width":e},"closeOthers":!1}}function f(){var e=$("#sidebar, .sidebar").first().width()||270;return{"position":{"my":"left top","at":"right center"},"css":{"min-width":e},"closeOthers":!1}}function h(e,t,n,a,i){if(e){var o=function(){var n=0,o=t.find(E),r=t.find(y),s=t.find(S);m(r,e.Title,p())?n++:k(t,r),i&&g(t,r,i.Title),m(s,e.Body,p())?n++:k(t,s),i&&g(t,s,i.Body),m(o,e.Tags,p())?n++:k(t,o),i&&g(t,o,i.Tags),m(t.find(C),e.EditComment,p())?n++:k(t,t.find(C)),m(t.find(T),e.Excerpt,p())?n++:k(t,t.find(T)),m(t.find(I),e.Email,f())?n++:k(t,t.find(I));var c=t.find(".general-error"),l=e.General&&e.General.length>0;if(l||n>0){if(!c.length){var u=t.find('input[type="submit"]:visible');u.before('<div class="general-error-container"><div class="general-error"></div><br class="cbt" /></div>'),c=t.find(".general-error")}if(l)m(c,e.General,{"position":"inline","css":{"float":"left","margin-bottom":"10px"},"closeOthers":!1,"dismissable":!1});else{k(t,c);var d;switch(a){case"question":d=function(e){return 1==e.specificErrorCount?"Your question couldn't be submitted. Please see the error above.":"Your question couldn't be submitted. Please see the errors above."}({"specificErrorCount":n});break;case"answer":d=function(e){return 1==e.specificErrorCount?"Your answer couldn't be submitted. Please see the error above.":"Your answer couldn't be submitted. Please see the errors above."}({"specificErrorCount":n});break;case"edit":d=function(e){return 1==e.specificErrorCount?"Your edit couldn't be submitted. Please see the error above.":"Your edit couldn't be submitted. Please see the errors above."}({"specificErrorCount":n});break;case"tags":d=function(e){return 1==e.specificErrorCount?"Your tags couldn't be submitted. Please see the error above.":"Your tags couldn't be submitted. Please see the errors above."}({"specificErrorCount":n});break;case"post":default:d=function(e){return 1==e.specificErrorCount?"Your post couldn't be submitted. Please see the error above.":"Your post couldn't be submitted. Please see the errors above."}({"specificErrorCount":n})}c.text(d)}}else t.find(".general-error-container").remove();var h;w()&&($("#sidebar").animate({"opacity":.4},500),h=setInterval(function(){w()||($("#sidebar").animate({"opacity":1},500),clearInterval(h))},500));var v;t.find(".validation-error").each(function(){var e=$(this).offset().top;(!v||v>e)&&(v=e)});var b=function(){for(var e=0;3>e;e++)t.find(".message").animate({"left":"+=5px"},100).animate({"left":"-=5px"},100)};if(v){var x=$(".review-bar").length;v=Math.max(0,v-(x?125:30)),$("html, body").animate({"scrollTop":v},b)}else b()},r=function(){1!=n||t.find(E).length?o():setTimeout(r,250)};r()}}function g(e,t,n){var a=p();if(a.type="warning",!n||0==n.length)return b(e,t),!1;var i=t.data("error-popup"),o=0;return i&&(o=i.height()+5),v(t,n,a,o)}function m(e,t,n){return n.type="error",v(e,t,n)}function v(e,t,n,a){var i,r=n.type;if(!(t&&0!=t.length&&e.length&&$("html").has(e).length))return!1;if(i=1==t.length?t[0]:"<ul><li>"+t.join("</li><li>")+"</li></ul>",i&&i.length>0){var s=e.data(r+"-popup");if(s&&s.is(":visible")){var c=e.data(r+"-message");if(c==i)return s.animateOffsetTop&&s.animateOffsetTop(a||0),!0;s.fadeOutAndRemove()}a>0&&(n.position.offsetTop=a);var l=StackExchange.helpers.showMessage(e,i,n);return l.find("a").attr("target","_blank"),l.click(o),e.addClass("validation-"+r).data(r+"-popup",l).data(r+"-message",i),!0}return!1}function b(e,t){x("warning",e,t)}function k(e,t){x("error",e,t)}function x(e,t,n){if(!n||0==n.length)return!1;var a=n.data(e+"-popup");return a&&a.is(":visible")&&a.fadeOutAndRemove(),n.removeClass("validation-"+e),n.removeData(e+"-popup"),n.removeData(e+"-message"),t.find(".validation-"+e).length||t.find(".general-"+e+"-container").remove(),!0}function w(){var e=!1,t=$("#sidebar, .sidebar").first();if(!t.length)return!1;var n=t.offset().left;return $(".message").each(function(){var t=$(this);return t.offset().left+t.outerWidth()>n?(e=!0,!1):void 0}),e}var y="input#title",S="textarea.wmd-input:first",E=".tag-editor",C="input[id^=edit-comment]",T="textarea#excerpt",I="input#m-address",M=[],A=250;return{"initOnBlur":e,"initOnBlurAndSubmit":t,"showErrorsAfterSubmission":h,"getSidebarPopupOptions":p}}();