package com.freshgrowth.comment;

import com.freshgrowth.comment.dto.CommentRequest;
import com.freshgrowth.common.AppException;
import com.freshgrowth.post.PostMapper;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CommentService {
    private final CommentMapper commentMapper;
    private final PostMapper postMapper;

    public CommentService(CommentMapper commentMapper, PostMapper postMapper) {
        this.commentMapper = commentMapper;
        this.postMapper = postMapper;
    }

    public List<Comment> findByPost(Long postId) {
        return commentMapper.findByPostId(postId);
    }

    @Transactional
    public Comment create(Long authorId, Long postId, CommentRequest request) {
        if (postMapper.findById(postId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "POST_NOT_FOUND", "게시글을 찾을 수 없습니다.");
        }
        Comment comment = new Comment();
        comment.setPostId(postId);
        comment.setParentId(resolveParentId(request.getParentId(), postId));
        comment.setAuthorId(authorId);
        comment.setContent(request.getContent());
        commentMapper.insert(comment);
        return commentMapper.findById(comment.getCommentId());
    }

    // 답글의 부모를 검증하고 1-depth로 평탄화한다.
    // 부모가 없거나 다른 게시글이면 무결성 오류로 막고, 부모가 이미 답글이면 그 루트에 붙인다.
    private Long resolveParentId(Long parentId, Long postId) {
        if (parentId == null) {
            return null;
        }
        Comment parent = commentMapper.findById(parentId);
        if (parent == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PARENT_COMMENT_NOT_FOUND",
                    "답글을 달 댓글을 찾을 수 없어요. 이미 삭제되었을 수 있어요.");
        }
        if (!parent.getPostId().equals(postId)) {
            throw new AppException(HttpStatus.BAD_REQUEST, "PARENT_POST_MISMATCH",
                    "다른 게시글의 댓글에는 답글을 달 수 없어요.");
        }
        // 대댓글에 다시 답글 → 최상위 댓글로 평탄화(트리 깊이 1 유지)
        return parent.getParentId() != null ? parent.getParentId() : parent.getCommentId();
    }

    @Transactional
    public Comment update(Long authorId, Long commentId, CommentRequest request) {
        if (commentMapper.findById(commentId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "COMMENT_NOT_FOUND", "댓글을 찾을 수 없습니다.");
        }
        if (commentMapper.update(commentId, authorId, request.getContent()) == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "수정 권한이 없습니다.");
        }
        return commentMapper.findById(commentId);
    }

    @Transactional
    public void delete(Long authorId, Long commentId) {
        if (commentMapper.findById(commentId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "COMMENT_NOT_FOUND", "댓글을 찾을 수 없습니다.");
        }
        if (commentMapper.delete(commentId, authorId) == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "삭제 권한이 없습니다.");
        }
    }
}
