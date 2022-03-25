// Copyright 2026 Dixmit
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

const {Component, useEffect, useRef, useState} = owl;

import {
    areDatesEqual,
    deserializeDate,
    deserializeDateTime,
    parseDate,
    parseDateTime,
    serializeDate,
    serializeDateTime,
} from "@web/core/l10n/dates";
import {formatDate, formatDateTime, formatFloat} from "@web/views/fields/formatters";

import {CheckBox} from "@web/core/checkbox/checkbox";
import {SelectMenu} from "@web/core/select_menu/select_menu";
import {TagsList} from "@web/core/tags_list/tags_list";

import {parseFloat} from "@web/views/fields/parsers";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useDateTimePicker} from "@web/core/datetime/datetime_picker_hook";
import {useInputField} from "@web/views/fields/input_field_hook";
import {useTagNavigation} from "@web/core/record_selectors/tag_navigation_hook";

export class LaboratoryValueField extends Component {
    setup() {
        super.setup(...arguments);
        this.numpadInputRef = useInputField({
            getValue: () => this.value,
            refName: "numpadDecimal",
            parse: (v) => {
                return {
                    ...this.props.record.data[this.props.name],
                    value: this.parse(v),
                };
            },
        });
        this.textInputRef = useInputField({
            getValue: () => this.value,
            refName: "textInput",
            parse: (v) => {
                return {...this.props.record.data[this.props.name], value: v};
            },
        });
        this.charInputRef = useInputField({
            getValue: () => this.value,
            refName: "charInput",
            parse: (v) => {
                return {...this.props.record.data[this.props.name], value: v};
            },
        });
        if (
            this.props.record.data[this.props.name].result_type === "datetime" ||
            this.props.record.data[this.props.name].result_type === "date"
        ) {
            const getPickerProps = () => {
                var value = this.props.record.data[this.props.name].value;
                if (value && typeof value === "string") {
                    if (
                        this.props.record.data[this.props.name].result_type === "date"
                    ) {
                        value = deserializeDate(value);
                    } else {
                        value = deserializeDateTime(value);
                    }
                }
                /** @type {DateTimePickerProps} */
                const pickerProps = {
                    value,
                    type: this.props.record.data[this.props.name].result_type,
                    range: false,
                    rounding: 0,
                };
                return pickerProps;
            };
            const dateTimePicker = useDateTimePicker({
                target: "root",
                showSeconds: true,
                get pickerProps() {
                    return getPickerProps();
                },
                onChange: () => {
                    this.state.range = false;
                },
                onClose: () => {
                    this.picker.activeInput = "";
                    this.state.value = deserializeDateTime(
                        this.props.record.data[this.props.name].value
                    );
                },
                onApply: async () => {
                    if (
                        this.props.record.data[this.props.name].result_type === "date"
                    ) {
                        await this.props.record.update({
                            [this.props.name]: {
                                ...this.props.record.data[this.props.name],
                                value: serializeDate(this.state.value),
                            },
                        });
                    } else {
                        await this.props.record.update({
                            [this.props.name]: {
                                ...this.props.record.data[this.props.name],
                                value: serializeDateTime(this.state.value),
                            },
                        });
                    }
                },
            });
            this.state = useState(dateTimePicker.state);
            this.picker = useState({activeInput: ""});
            this.openPicker = dateTimePicker.open;
            this.dateInput = useRef("dateInput");
            useEffect(
                () => {
                    if (
                        this.dateInput.el?.getAttribute("data-field") ===
                        this.picker.activeInput
                    ) {
                        this.dateInput.el.focus();
                        this.openPicker();
                    }
                },
                () => [this.dateInput.el?.tagName, this.picker.activeInput]
            );
        }
        if (this.type === "multiselection") {
            useTagNavigation("multiselectionInput", {
                isEnabled: () => !this.props.readonly,
                delete: (index) => this.deleteTagByIndex(index),
            });
        }
    }
    get type() {
        return this.props.record.data[this.props.name].result_type;
    }
    parse(value) {
        if (this.type === "float") {
            return parseFloat(value, {allowOperation: true});
        }
        if (this.type === "text" || this.type === "char") {
            return value.trim();
        }
        if (this.type === "date") {
            return formatDate(value);
        }
        if (this.type === "datetime") {
            return formatDateTime(value);
        }
        return value;
    }
    get value() {
        const data = this.props.record.data[this.props.name];
        if (this.type === "float") {
            return formatFloat(data.value || 0, {digits: [16, data.digits || 0]});
        }
        if (this.type === "boolean") {
            return data.value;
        }

        if (this.type === "date" && data.value) {
            return formatDate(deserializeDate(data.value), {numeric: true});
        }
        if (this.type === "datetime" && data.value) {
            return formatDateTime(deserializeDateTime(data.value), {numeric: true});
        }
        return data.value || "";
    }
    onChangeBoolean(newValue) {
        this.props.record.update({
            [this.props.name]: {
                ...this.props.record.data[this.props.name],
                value: this.parse(newValue),
            },
        });
    }
    triggerDateIsDirty(isDirty) {
        this.props.record.model.bus.trigger(
            "FIELD_IS_DIRTY",
            isDirty ??
                !areDatesEqual(
                    this.props.record.data[this.props.name].value,
                    this.state.value
                )
        );
    }
    get formattedDate() {
        var formattedValue = false;
        if (this.state.value && this.type === "date") {
            formattedValue = formatDate(this.state.value, {
                numeric: true,
            });
        } else if (this.state.value && this.type === "datetime") {
            formattedValue = formatDateTime(this.state.value, {
                numeric: true,
            });
        }
        return formattedValue;
    }
    onDateInput() {
        this.triggerDateIsDirty(true);
    }
    async onDateChange() {
        const value = this.dateInput.el.value;
        if (!value) {
            this.state.value = null;
            this.triggerDateIsDirty(false);
            return;
        }
        if (this.type === "date") {
            this.state.value = parseDate(value);
            await this.props.record.update({
                [this.props.name]: {
                    ...this.props.record.data[this.props.name],
                    value: serializeDate(this.state.value),
                },
            });
        } else if (this.type === "datetime") {
            this.state.value = parseDateTime(value);
            await this.props.record.update({
                [this.props.name]: {
                    ...this.props.record.data[this.props.name],
                    value: serializeDateTime(this.state.value),
                },
            });
        }
    }
    onChangeMultiSelectionCheck(value) {
        this.props.record.update({
            [this.props.name]: {
                ...this.props.record.data[this.props.name],
                value: {
                    ...this.props.record.data[this.props.name].value,
                    [value]: !this.props.record.data[this.props.name].value?.[value],
                },
            },
        });
    }
    onChangeSelection(value) {
        this.props.record.update({
            [this.props.name]: {
                ...this.props.record.data[this.props.name],
                value: value,
            },
        });
    }
}

LaboratoryValueField.template = "lims.LaboratoryValueField";
LaboratoryValueField.components = {CheckBox, SelectMenu, TagsList};
LaboratoryValueField.props = {
    ...standardFieldProps,
};
export const laboratoryValueField = {
    component: LaboratoryValueField,
    supportedTypes: ["json"],
};

registry.category("fields").add("laboratory_value", laboratoryValueField);
