from scripts import (
    generate_engraving_defaults_mapping_table,
    generate_error_key_literal,
    generate_error_templates_table,
    generate_options_table,
)

if __name__ == "__main__":
    generate_engraving_defaults_mapping_table.main()
    generate_error_key_literal.main()
    generate_error_templates_table.main()
    generate_options_table.main()
