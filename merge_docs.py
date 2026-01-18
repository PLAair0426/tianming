import os

def read_file(path):
    encodings = ['utf-8', 'gb18030', 'gbk', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
                print(f"Successfully read {path} using {enc}")
                return content
        except UnicodeDecodeError:
            continue
        except UnicodeError:
             continue
    
    print(f"FAILED to read {path}. Dumping first 20 bytes:")
    try:
        with open(path, 'rb') as f:
            print(f.read(20))
    except Exception as e:
        print(f"Could not read binary: {e}")
    return None

def main():
    base_dir = r"h:\天国神算"
    readme_path = os.path.join(base_dir, "README.md")
    
    files_to_merge = [
        "API限流实现总结.md",
        "多人使用问题分析.md",
        "并发处理优化说明.md",
        "用户隔离原理说明.md",
        "用户隔离实现指南.md",
        "用户隔离测试指南.md",
        "防止单用户占用资源方案.md"
    ]
    
    print("--- START MERGE ---")
    
    readme_content = ""
    if os.path.exists(readme_path):
        readme_content = read_file(readme_path)
        if readme_content is None:
             print("Aborting merge because README.md could not be read.")
             return
    else:
        print("README.md not found, creating new.")
        readme_content = "# Pneuma Project Documentation\n\n"

    final_content = readme_content

    for fname in files_to_merge:
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            print(f"Merging {fname}...")
            c = read_file(fpath)
            if c:
                final_content += "\n\n---\n\n" 
                final_content += c
            else:
                print(f"Skipping {fname} (encoding error)")
        else:
            print(f"Warning: {fname} not found.")

    # Write back
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("Successfully merged content to README.md")

if __name__ == "__main__":
    main()
