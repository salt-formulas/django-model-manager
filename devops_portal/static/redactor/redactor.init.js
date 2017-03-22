
/**
This makes sure that we initialise the redactor on the text area once its displayed
so it can be used as part of an inline formset.

Credit to the approach taken in:
https://github.com/yourlabs/django-autocomplete-light
**/
jQuery(document).ready(function() {
    jQuery('textarea.redactor-box').on('initialize', function() {
        redactor_options = jQuery(this).data('redactor-options');
        redactor_options.imageUploadErrorCallback = function (json) {
            // TODO: Needs better error messages
            alert(json.error);
        }
        jQuery(this).redactor(redactor_options);
    });
    jQuery(document).trigger('redactorWidgetReady');

    jQuery('textarea.redactor-box:not([id*="__prefix__"])').each(function() {
        jQuery(this).trigger('initialize');
    });

     jQuery(document).bind('DOMNodeInserted', function(e) {
        var widget = jQuery(e.target).find('.redactor-box');

        if (!widget.length) return;

        widget.trigger('initialize');
    });

  /* patch Horizon init to bind redactor */
  horizon.modals.addModalInitFunction(function (modal) {
    $(modal).find(":text, select, textarea").filter(":visible:first").focus();
    $(modal).find('textarea.redactor-box').each(function(index) {
        redactor_options = jQuery(this).data('redactor-options');
        redactor_options.imageUploadErrorCallback = function (json) {
            // TODO: Needs better error messages
            alert(json.error);
        }
        jQuery(this).redactor(redactor_options);
    });
  });
});