from models import SQLHandler


def main():
    handler = SQLHandler()
    handler.connect_table('job_postings')
    flag = True
    counter = 0
    c = 0

    while flag:
        row = handler.return_row()
        c += 1

        if row is None:
            flag = False
            continue

        if row[6] == 'en' and row[7] is None:
            handler.update_column('job_postings',
                                   row[0],
                                   'text_en',
                                   row[5])
            counter += 1

        if c % 100 == 0:
            print(('\n\n- - - - - - - - - -'
                   'X X X X X X X X X X'
                   'DONE {}'
                   'X X X X X X X X X X'
                   '- - - - - - - - - -\n\n').format(c))

    print(counter + 355)


if __name__ == '__main__':
    main()