import os

def generate_bindings_cpp(struct_names, output_dir="."):
    lines = [
        "// Auto-generated bindings.cpp",
        "#include <pybind11/pybind11.h>",
        "#include <pybind11/stl.h>  // For STL to Python conversions, including std::map and std::vector",
        "#include <nlohmann/json.hpp>  // Required for nlohmann::json",
    ]

    # Include all publisher/subscriber implementations
    for struct in struct_names:
        lines.append(f'#include "{struct}Publisher.cpp"')
        lines.append(f'#include "{struct}Subscriber.cpp"')

    lines.append("\nnamespace py = pybind11;")
    lines.append("PYBIND11_MODULE(ddspython, m) {")
    lines.append('    m.doc() = "Unified DDS Python Bindings Module";')

    # Call the binding functions
    for struct in struct_names:
        lines.append(f"    bind_{struct}Publisher(m);")
        lines.append(f"    bind_{struct}Subscriber(m);")

    lines.append("}")

    # Write to file
    bindings_path = os.path.join(output_dir, "bindings.cpp")
    with open(bindings_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated {bindings_path}")
