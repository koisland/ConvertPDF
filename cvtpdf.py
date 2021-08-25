import os
import shutil
import argparse

import pdf2image


def uniq_fname(path, _num_suffix=2):
    """
    Recursive function to find unique filenames/directories.
    :param path: fname/dir path
    :param _num_suffix: number to start on for duplicates.
    :return:
    """
    fname, ext = os.path.splitext(path)
    mod_path = f"{fname}_{_num_suffix}{ext}"

    # check if unmodified path exists.
    if not os.path.exists(path):
        return path
    # if above fails, check if modified path exists.
    if not os.path.exists(mod_path):
        return mod_path
    else:
        # if the modified path exists, increment the number suffix by 1 and recursively call function.
        _num_suffix += 1
        return uniq_fname(path, _num_suffix)


def main(args):
    output_path = os.getcwd() if args["output"] == "cwd" else args["output"]
    filename, _ = os.path.splitext(args["input"])
    pdf_path = os.path.join(os.getcwd(), str(args["input"]))
    print(pdf_path)

    if not os.path.exists(pdf_path):
        print("PDF file doesn't exist.")
        return

    # get info from pdf as dict.
    pdf_info = pdf2image.pdfinfo_from_path(pdf_path)

    # check if pdf has more than one page. create folder if true and set as dest.
    if multiple_pages := pdf_info.get("Pages") > 1:
        dest = os.path.join(output_path, filename)
        print(dest)

        # check if dest is unique. otherwise, create new filename.
        dest = uniq_fname(dest)

        # make dir
        os.mkdir(dest)
    # otherwise, dest is the current working directory.
    else:
        dest = output_path

    # convert pdf images to pil images and loop through and save them as pngs
    imgs = pdf2image.convert_from_path(pdf_path)
    if multiple_pages:
        for i, img in enumerate(imgs, 1):
            img_path = os.path.join(dest, f'{filename}_{i}.{args["ftype"]}')
            img.save(img_path)

        # zip file if desired.
        if args["zip"] == "True":
            # check if new zip is unique
            new_dest = uniq_fname(f"{filename}.zip")
            filename, _ = os.path.splitext(new_dest)

            # zip dir
            new_dest = shutil.make_archive(filename, 'zip', dest)

            # recursively removes original dest WITH files in it.
            shutil.rmtree(dest)

            # declare new_dest as dest
            dest = new_dest

        print(f"Saved to {dest}.")
    else:
        img_path = os.path.join(dest, f'{filename}{args["ftype"]}')

        # check if img filename is unique and create new one if not.
        img_path = uniq_fname(img_path)

        # save img
        imgs[0].save(img_path)
        print(f"Saved to {os.path.join(dest, img_path)}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a pdf to images.")
    parser.add_argument("--input", "-i", help="Path to pdf file.")
    parser.add_argument("--output", "-o", help="Path to output dir.", default="cwd")
    parser.add_argument("--ftype", "-f", help="Image file extension to save as.", default=".png")
    parser.add_argument("--zip", "-z", help="Zip resulting folder?", default="False")
    main(vars(parser.parse_args()))
