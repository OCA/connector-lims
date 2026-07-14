// Copyright 2026 Dixmit
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

const {Component} = owl;
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class LaboratoryEvaluationField extends Component {
    get value() {
        return this.props.record.data[this.props.name];
    }
}
LaboratoryEvaluationField.template = "lims.LaboratoryEvaluationField";
LaboratoryEvaluationField.props = {
    ...standardFieldProps,
};
export const laboratoryEvaluationField = {
    component: LaboratoryEvaluationField,
    supportedTypes: ["selection"],
};

registry.category("fields").add("laboratory_evaluation", laboratoryEvaluationField);
