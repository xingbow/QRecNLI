import { getColumnType, type2icon } from './utils.js'

export default {
    functional: true,
    props: ['condUnit', 'tables'],
    render(h, { props, data, children }) {
        const [notOp, opId, valUnit, val1, val2] = props.condUnit;
        const [unitOp, colUnit1, colUnit2] = valUnit;
        const [innerAggId, colToken, isDistinct] = colUnit1
        // TODO: ignore col_unit2
        const innerAggToken = (innerAggId && innerAggId !== "none") ? innerAggId : "";

        const type = getColumnType(colToken, props.tables);

        return <div class="cond-unit-token">
          {innerAggToken && <span class="agg-text">{innerAggToken}</span>}
          <div class="col-token">
            <i class={type2icon(type)} />
            <span class="col-text">{colToken}</span>
          </div>
        </div>;
    }
}