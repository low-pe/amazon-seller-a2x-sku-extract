import os

def remove_lines_with_keywords(file_path, keywords):
    # Backup original file
    backup_path = file_path + ".bak"
    os.rename(file_path, backup_path)

    with open(backup_path, 'r') as infile:
        lines = infile.readlines()

    removed_lines = []
    filtered_lines = []

    for line in lines:
        if any(keyword in line for keyword in keywords):
            removed_lines.append(line)
        else:
            filtered_lines.append(line)

    with open(file_path, 'w') as outfile:
        outfile.writelines(filtered_lines)

    print(f"\n✅ Done! Lines containing your keywords were removed.")
    print(f"📦 Original file backed up to: {backup_path}")

    if removed_lines:
        print("\n🧹 Removed lines:")
        for line in removed_lines:
            print(line.strip())
    else:
        print("\nNo lines matched the given keywords.")

if __name__ == "__main__":
    print("📥 Paste your list of keywords (one per line). Press Enter twice when done:")
    keywords_input = []
    while True:
        line = input()
        if line == "":
            break
        keywords_input.append(line.strip())

    file_path = input("📄 Enter the path to the file you want to clean: ").strip()

    if not os.path.isfile(file_path):
        print("❌ That file does not exist.")
    else:
        remove_lines_with_keywords(file_path, keywords_input)
