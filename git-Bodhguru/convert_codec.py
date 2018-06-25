import sys
import os
path_of_content = "/home/kolibri/Documents/Final_Bodhaguru/Hindi/"
count = 0
video_path = []
for folder in os.listdir(path_of_content):
    path = path_of_content+folder+'/'

    for subfolder in os.listdir(path):
        path1 = path + subfolder+'/'

        for subfolder1 in os.listdir(path1):
            path2 = path1+subfolder1+'/'

            for subfolder2 in os.listdir(path2):
                path3 = path2+subfolder2+'/'

                for subfolder3 in os.listdir(path3):
                    if subfolder3.endswith('_.mp4'):
                        print("Already codec is converted::::",path3+subfolder3)
                    elif subfolder3.endswith('.mp4'):
                        final_path = (path3+subfolder3).replace(' ','\ ')
                        dest_path = final_path.replace(".mp4","_.mp4")
                        print(dest_path)
                        command = "ffmpeg -i "+final_path+" "+dest_path+" -hide_banner"
                        print(command)                        
                        os.system(command)
                        print(final_path)
                        remove_path = final_path.replace('\ ',' ')
                        os.remove(remove_path)
                        #name = dest_path.replace("_.mp4",".mp4")
                        #os.rename(dest_path,name)
                        count = count + 1
                        print(count)
                        print("*************Conversion Done:::::", dest_path)
