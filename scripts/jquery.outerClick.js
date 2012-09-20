/*
*	jQuery custom event 'outerclick'
*	based on (updated, fixed): http://littleroom.se/playground/outerClick/outerClick.js
*   Copyright (c) 2010 Daniel Steigerwald (http://daniel.steigerwald.cz), Mit Style License
*/

(function ($) {

	var elements = [],

	check = function (e) {
		for (var i = 0, l = elements.length; i < l; i++) {
			var el = elements[i];
			if (el == e.target || $.contains(el, e.target)) continue;
			$.event.trigger('outerclick', e, el);
		}
	},

	self = $.event.special.outerclick = {

		setup: function () {
			var i = elements.length;
			if (!i) $.event.add(document, 'click touchend', check);
			if ($.inArray(this, elements) < 0)
				elements[i] = this;
		},

		teardown: function () {
			var i = $.inArray(this, elements);
			if (i < 0) return;
			elements.splice(i, 1);
			if (!elements.length)
				$.event.remove(document, 'click touchend', check);
		}

	};

	$.fn.outerclick = function (fn) {
		return fn === undefined
			? this.trigger('outerclick')
			: this.length ? this.each(function () {
				$(this).bind('outerclick', fn);
			}) : this;
	};

})(jQuery);