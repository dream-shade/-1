#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* create_node(int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = value;
    new_node->next = NULL;
    return new_node;
}

// 核心函数：从文件读取数据并建链表
Node* load_from_file(const char* filename) {
    FILE* fp = fopen(filename, "r");
    if (fp == NULL) {
        printf("文件打开失败\n");
        return NULL;
    }
    
    Node* head = NULL;
    Node* tail = NULL;
    int val;
    
    // fscanf 返回成功读取的变量个数，读到文件末尾会返回 EOF
    while (fscanf(fp, "%d", &val) != EOF) {
        Node* new_node = create_node(val);
        if (head == NULL) {
            head = new_node;
            tail = new_node;
        } else {
            tail->next = new_node;
            tail = new_node;
        }
    }
    fclose(fp);
    return head;
}
void save_list_to_file(Node* head, const char* filename) {
    FILE* fp = fopen(filename, "w");     // "w" = 写（覆盖）
    if (fp == NULL) {
        printf("文件创建失败\n");
        return;
    }

    Node* current = head;                // 用临时指针走
    while (current != NULL) {
        fprintf(fp, "%d ", current->data);  // 写进文件
        current = current->next;            // 走向下一个人
    }
    fprintf(fp, "\n");
    fclose(fp);
}
void free_list(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* next = current->next;   // ← 先记住下一个人！
        free(current);                // 拆掉当前的人
        current = next;               // 走过去
    }
}
int main() {
    // 先在代码目录下建个 nums.txt，里面随便写几个数字，比如：10 20 30 40
    Node* my_list = load_from_file("nums.txt");
    
    // 遍历打印验证
    Node* current = my_list;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
    return 0;
}
