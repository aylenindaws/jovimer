odoo.define('indaws_affinity_so_availability_icon.widget_qty_at_date', function (require) {
    'use strict';


    const QtyAtDateWidget = require('sale_stock.QtyAtDateWidget');
    const session = require('web.session');

    QtyAtDateWidget.include({
        willStart: function () {
            var self = this;
            var superDef = this._super.apply(this, arguments);
            var def = self._rpc(
                {
                    model: 'stock.move',
                    method: 'search',
                    args: [[
                    ['product_id.id', '=', self.data.product_id.data ? self.data.product_id.data.id : false],
                    ['state', '=', 'assigned'],
                    ['picking_code', '=', 'incoming'],
                    ]],
                }).then(function (move){
                    if(move.length !== 0){
                        self['comfirm_po_move'] = true
                    }
                    else{
                        self['comfirm_po_move'] = false
                    }
                    self.data.comfirm_po_move = self.comfirm_po_move;
                });
            return Promise.all([superDef, def]);
        },
    });


});
