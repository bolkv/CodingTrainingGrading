import os
import zipfile
import subprocess

def modify_code_for_scanf(cpp_file_path):
    try:
        with open(cpp_file_path, 'r', encoding='utf-8') as file:
            code = file.read()
    except UnicodeDecodeError:
        with open(cpp_file_path, 'r', encoding='euc-kr') as file:
            code = file.read()
    
    modified_code = code.replace("scanf_s", "scanf")

    with open(cpp_file_path, 'w', encoding='utf-8') as file:
        file.write(modified_code)

def unzip_files_in_folder(folder_path, file):
    cpp_files = []
    missing_files = []
    
    for file_name in os.listdir(folder_path):
        temp = file_name.split("_")
        student_name = os.path.splitext(temp[2])[0]
        found = False
        if file_name.endswith('.zip'):
            zip_file_path = os.path.join(folder_path, file_name)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    # 폴더 경로와 상관없이 파일 이름만 추출하여 비교
                    base_name = os.path.basename(member)
                    if base_name == file or base_name == file.replace(".cpp", ".c") in base_name:
                        new_file_name = f"{student_name}_{base_name}"
                        extracted_path = os.path.join(folder_path, new_file_name)
                        
                        # 파일을 추출
                        with open(extracted_path, 'wb') as f_out:
                            f_out.write(zip_ref.read(member))
                        
                        modify_code_for_scanf(extracted_path)
                        
                        cpp_files.append((extracted_path, student_name))
                        found = True
                        break  # 파일을 찾았으므로 나머지 ZIP 파일 내용은 무시
            
            # 파일을 찾지 못한 경우 missing_files에 추가
            if not found:
                missing_files.append(student_name)
    
    return cpp_files, missing_files

def run_executable(executable_path, input_data=None):
    try:
        if isinstance(input_data, str):
            input_data = input_data.encode('utf-8')
        
        process = subprocess.Popen([executable_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=input_data)
        
        if process.returncode != 0:
            print(f"실행 오류: {executable_path}")
            print(stderr.decode('utf-8'))
            return None
        
        return stdout.decode('utf-8')
        
    except Exception as e:
        print(f"실행 중 오류: {executable_path}, {e}")
        return None

def compile_cpp_file(cpp_file_path):
    executable_name = os.path.splitext(cpp_file_path)[0]
    compile_command = ["g++", cpp_file_path, "-o", executable_name]
    
    result = subprocess.run(compile_command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"컴파일 오류: {cpp_file_path}")
        print(result.stderr)
        return None
    return executable_name

def main(folder_path, input_data, file):
    cpp_files, missing_files = unzip_files_in_folder(folder_path, file)

    if missing_files:
        print("파일을 찾지 못한 학생 목록:")
        for student_name in sorted(missing_files):
            print(f"- {student_name}")
        print("===========================================\n")

    # 학생 이름을 기준으로 cpp_files 리스트를 정렬
    cpp_files.sort(key=lambda x: x[1])

    for cpp_file, student_name in cpp_files:
        print(f"학생 이름: {student_name}")
        student_exe_file = compile_cpp_file(cpp_file)
        if student_exe_file:
            student_output = run_executable(student_exe_file, input_data)
            print(student_output)
            os.remove(student_exe_file)
            os.remove(cpp_file)

        print("===========================================\n")


folder_path = "/mnt/d/채점/temp"
file = input("채점할 소스코드 명을 입력하세요: ")
input_data = input("input 값을 입력하세요: ")
main(folder_path, input_data, file)
