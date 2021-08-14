import {getColumnType} from './utils.js'

export default {
  functional: true,
  props: ['selectUnit', 'tables'],
  render(h, { props, data, children }) {
    const [aggId, valUnit] = props.selectUnit;
    const [unitOp, colUnit1, colUnit2] = valUnit;
    const [innerAggId, colToken, isDistinct] = colUnit1
    // TODO: ignore col_unit2
    const aggToken = (aggId && aggId !== "none") ? aggId : "";
    const innerAggToken = (innerAggId && innerAggId !== "none") ? innerAggId : "";

    console.log(getColumnType);
    const type = getColumnType(colToken, props.tables);

    return <div class="select-token">
      <span>{aggToken}</span>
      <span>{innerAggToken}</span>
      <div class="col-token">
        <i class={type == "text" ? "fas fa-font" : "fas fa-list-ol"} />
        <span class="col-text">{colToken}</span>
      </div>
    </div>;
  }
}