import {animationFrame, beforeEach, click, edit, expect, test} from "@odoo/hoot";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";
import {mockTimeZone} from "@odoo/hoot-mock";

class TestLine extends models.Model {
    _name = "lims.test.line";

    value = fields.Json({});
    _records = [
        {
            id: 1,
            value: {
                value: 1,
                result_type: "float",
                digits: 0,
            },
        },
        {
            id: 2,
            value: {
                value: 2,
                result_type: "float",
                digits: 3,
            },
        },
        {
            id: 3,
            value: {
                value: "String Value",
                result_type: "char",
            },
        },
        {
            id: 4,
            value: {
                value: "String\nValue",
                result_type: "text",
            },
        },
        {
            id: 5,
            value: {
                value: "2024-06-01",
                result_type: "date",
            },
        },
        {
            id: 6,
            value: {
                value: "2024-06-01 02:00:00",
                result_type: "datetime",
            },
        },
        {
            id: 7,
            value: {
                value: "option1",
                result_type: "selection",
                selection: ["option1", "option2", "option3"],
            },
        },
        {
            id: 8,
            value: {
                value: ["option1", "option3"],
                result_type: "multiselection",
                selection: ["option1", "option2", "option3"],
            },
        },
        {
            id: 9,
            value: {
                value: {
                    option1: true,
                    option2: false,
                    option3: true,
                },
                result_type: "multiselection-check",
            },
        },
        {
            id: 10,
            value: {
                value: true,
                result_type: "boolean",
            },
        },
    ];
    _views = {
        list: `
            <list editable="bottom">
                <field name="value" widget="laboratory_value"/>
            </list>
        `,
    };
}
defineModels([TestLine]);
defineMailModels();

beforeEach(() => {
    mockTimeZone(-5);
});

test("Review Readonly Render of LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(1) .o_field_laboratory_value").toHaveText("1");
    expect("tbody tr:nth-child(2) .o_field_laboratory_value").toHaveText("2.000");
    expect("tbody tr:nth-child(3) .o_field_laboratory_value").toHaveText(
        "String Value"
    );
    expect("tbody tr:nth-child(4) .o_field_laboratory_value").toHaveText(
        "String\nValue"
    );
    expect("tbody tr:nth-child(5) .o_field_laboratory_value").toHaveText("06/01/2024");
    expect("tbody tr:nth-child(6) .o_field_laboratory_value").toHaveText(
        "05/31/2024 21:00:00"
    );
    expect("tbody tr:nth-child(7) .o_field_laboratory_value").toHaveText("option1");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(1)"
    ).toHaveText("option1");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(2)"
    ).toHaveText("option3");
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(1).selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(2).not-selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(3).selected"
    ).toHaveCount(1);
    expect("tbody tr:nth-child(10) .o_field_laboratory_value input").toBeChecked();
});
test("Review Writing Float on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(1) .o_field_laboratory_value").toHaveText("1");
    expect("tbody tr:nth-child(2) .o_field_laboratory_value").toHaveText("2.000");
    await click("tbody tr:nth-child(1) .o_field_laboratory_value");
    await animationFrame();
    await edit("100.1");
    await click("tbody tr:nth-child(2) .o_field_laboratory_value");
    await animationFrame();
    expect("tbody tr:nth-child(1) .o_field_laboratory_value").toHaveText("100");
    await edit("100.1");
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(1) .o_field_laboratory_value").toHaveText("100");
    expect("tbody tr:nth-child(2) .o_field_laboratory_value").toHaveText("100.100");
});
test("Review Writing Char on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(3) .o_field_laboratory_value").toHaveText(
        "String Value"
    );
    await click("tbody tr:nth-child(3) .o_field_laboratory_value");
    await animationFrame();
    await edit("New String");
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(3) .o_field_laboratory_value").toHaveText("New String");
});
test("Review Writing Text on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(4) .o_field_laboratory_value").toHaveText(
        "String\nValue"
    );
    await click("tbody tr:nth-child(4) .o_field_laboratory_value");
    await animationFrame();
    await edit("New String\nWith Multiple Lines\nTo Test Textarea");
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(4) .o_field_laboratory_value").toHaveText(
        "New String\nWith Multiple Lines\nTo Test Textarea"
    );
});
test("Review Writing Date on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(5) .o_field_laboratory_value").toHaveText("06/01/2024");
    await click("tbody tr:nth-child(5) .o_field_laboratory_value");
    await animationFrame();
    await edit("06/15/2024");
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(5) .o_field_laboratory_value").toHaveText("06/15/2024");
});
test("Review Writing DateTime on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(6) .o_field_laboratory_value").toHaveText(
        "05/31/2024 21:00:00"
    );
    await click("tbody tr:nth-child(6) .o_field_laboratory_value");
    await animationFrame();
    await edit("06/15/2024");
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(6) .o_field_laboratory_value").toHaveText(
        "06/15/2024 00:00:00"
    );
});
test("Review Writing Selection on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(7) .o_field_laboratory_value").toHaveText("option1");
    await click("tbody tr:nth-child(7) .o_field_laboratory_value");
    await animationFrame();
    await click("tbody tr:nth-child(7) .o_field_laboratory_value input");
    await animationFrame();
    await click(".o_popover .o-dropdown-item:nth-child(4)");
    await animationFrame();
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(7) .o_field_laboratory_value").toHaveText("option3");
});
test("Review Writing Multi-Selection on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(8) .o_field_laboratory_value .o_tag").toHaveCount(2);
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(1)"
    ).toHaveText("option1");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(2)"
    ).toHaveText("option3");
    await click("tbody tr:nth-child(8) .o_field_laboratory_value");
    await animationFrame();
    await click("tbody tr:nth-child(8) .o_field_laboratory_value input");
    await animationFrame();
    await click(".o_popover .o-dropdown-item:nth-child(3)");
    await animationFrame();
    expect("tbody tr:nth-child(8) .o_field_laboratory_value .o_tag").toHaveCount(3);
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(1)"
    ).toHaveText("option1");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(2)"
    ).toHaveText("option3");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(3)"
    ).toHaveText("option2");
    await click(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(2) .o_delete"
    );
    await animationFrame();
    expect("tbody tr:nth-child(8) .o_field_laboratory_value .o_tag").toHaveCount(2);
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(1)"
    ).toHaveText("option1");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(2)"
    ).toHaveText("option2");
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(8) .o_field_laboratory_value .o_tag").toHaveCount(2);
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(1)"
    ).toHaveText("option1");
    expect(
        "tbody tr:nth-child(8) .o_field_laboratory_value .o_tag:nth-child(2)"
    ).toHaveText("option2");
});
test("Review Writing Multi-Selection with Checks on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(1).selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(2).not-selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(3).selected"
    ).toHaveCount(1);
    await click("tbody tr:nth-child(9) .o_field_laboratory_value");
    await animationFrame();
    await click("tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(2)");
    await animationFrame();
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(1).selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(2).selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(3).selected"
    ).toHaveCount(1);
    await click("tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(1)");
    await animationFrame();
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(1).not-selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(2).selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(3).selected"
    ).toHaveCount(1);
    await click(".o_list_button_save");
    await animationFrame();
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(1).not-selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(2).selected"
    ).toHaveCount(1);
    expect(
        "tbody tr:nth-child(9) .o_field_laboratory_value ul li:nth-child(3).selected"
    ).toHaveCount(1);
});
test("Review Writing Boolean on LIMS", async () => {
    await mountView({
        type: "list",
        resModel: "lims.test.line",
    });
    expect(".o_field_laboratory_value").toHaveCount(10);
    expect("tbody tr:nth-child(10) .o_field_laboratory_value input").toBeChecked();
    await click("tbody tr:nth-child(10) .o_field_laboratory_value");
    await animationFrame();
    await click("tbody tr:nth-child(10) .o_field_laboratory_value .o-checkbox");
    await animationFrame();
    expect("tbody tr:nth-child(10) .o_field_laboratory_value input").not.toBeChecked();
    await click(".o_list_button_save");
    await animationFrame();
    expect("tbody tr:nth-child(10) .o_field_laboratory_value input").not.toBeChecked();
});
