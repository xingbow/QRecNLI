import { getColumnType, type2icon } from './utils.js'

export const ColUnitToken = {
  functional: true,
  props: ['colUnit', 'tables'],
  render(h, { props, data, children }) {
    const [aggId, colToken, isDistinct] = props.colUnit;
    // TODO: ignore col_unit2
    const aggToken = (aggId && aggId !== "none") ? aggId : "";

    const type = getColumnType(colToken, props.tables);

    return <div class="cond-unit-token">
      {aggToken && <span class="agg-text">{aggToken}</span>}
      <div class="col-token">
        <i class={type2icon(type)} />
        <span class="col-text">{colToken}</span>
      </div>
    </div>;
}
}

export const CondUnitToken = {
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

export const SelectToken = {
  functional: true,
  props: ['selectUnit', 'tables'],
  render(h, { props, data, children }) {
    const [aggId, valUnit] = props.selectUnit;
    const [unitOp, colUnit1, colUnit2] = valUnit;
    const [innerAggId, colToken, isDistinct] = colUnit1
    // TODO: ignore col_unit2
    const aggToken = (aggId && aggId !== "none") ? aggId : undefined;
    const innerAggToken = (innerAggId && innerAggId !== "none") ? innerAggId : undefined;

    const type = getColumnType(colToken, props.tables);

    return <div class="select-token">
      {aggToken && <span class="agg-text">{aggToken}</span>}
      {innerAggToken && <span class="agg-text">{innerAggToken}</span>}
      <div class="col-token">
        <i class={type2icon(type)} />
        <span class="col-text">{colToken}</span>
      </div>
    </div>;
  }
}